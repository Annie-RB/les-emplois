import re
from copy import deepcopy

from django.conf import settings
from django.core import mail
from django.core.mail import get_connection
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import EmailMessage
from django.template.loader import get_template
from huey.contrib.djhuey import task

from itou.utils.iterators import chunks


# This is the "real" email backend used by the async wrapper / email backend
ASYNC_EMAIL_BACKEND = "anymail.backends.mailjet.EmailBackend"


def remove_extra_line_breaks(text):
    """
    Replaces multiple line breaks with just one.

    Useful to suppress empty line breaks generated by Django's template tags
    in emails text templates.
    """
    return re.sub(r"\n{3,}", "\n\n", text)


def get_email_text_template(template, context):
    context.update(
        {
            "itou_protocol": settings.ITOU_PROTOCOL,
            "itou_fqdn": settings.ITOU_FQDN,
            "itou_email_assistance": settings.ITOU_EMAIL_ASSISTANCE,
            "itou_email_contact": settings.ITOU_EMAIL_CONTACT,
            "itou_environment": settings.ITOU_ENVIRONMENT,
        }
    )
    return remove_extra_line_breaks(get_template(template).render(context).strip())


def get_email_message(to, context, subject, body, from_email=settings.DEFAULT_FROM_EMAIL, bcc=None):
    subject_prefix = "[DEMO] " if settings.ITOU_ENVIRONMENT == "DEMO" else ""
    return mail.EmailMessage(
        from_email=from_email,
        to=to,
        bcc=bcc,
        subject=subject_prefix + get_email_text_template(subject, context),
        body=get_email_text_template(body, context),
    )


# Mailjet max number of recipients (CC, BCC, TO)
_MAILJET_MAX_RECIPIENTS = 50


def sanitize_mailjet_recipients(email_message):
    """
    Mailjet API has a **50** number limit for anytype of email recipient:
    * TO
    * CC
    * BCC

    This function:
    * partitions email recipients with more than 50 elements
    * creates new emails with a number of recipients in the Mailjet limit
    * **only** checks for `TO` recipients owerflows

    `email_message` is an EmailMessage object (not serialized)

    Returns a **list** of "sanitized" emails.
    """

    if len(email_message.to) <= _MAILJET_MAX_RECIPIENTS:
        # We're ok, return a list containing the original message
        return [email_message]

    sanitized_emails = []
    part_to = chunks(email_message.to, _MAILJET_MAX_RECIPIENTS)
    # We could also combine to, cc and bcc, but it's useless for now

    for tos in part_to:
        copy_email = deepcopy(email_message)
        copy_email.to = list(tos)
        sanitized_emails.append(copy_email)

    return sanitized_emails


# Custom async email backend wrapper
# ----------------------------------

# Settings are explicit for humans, but this is what Huey needs
_NB_RETRIES = int(
    settings.SEND_EMAIL_RETRY_TOTAL_TIME_IN_SECONDS / settings.SEND_EMAIL_DELAY_BETWEEN_RETRIES_IN_SECONDS
)


def _serializeEmailMessage(email_message):
    """
    Returns a dict with `EmailMessage` instance content serializable via Pickle (remote data sending concern).

    **Important:**
    Some important features & fields of `EmailMessage` are not "serialized":
    * attachments
    * special options of the messages

    Just the bare minimum used by the app is kept for serialization.

    This functions works in pair with `_deserializeEmailMessage`.
    """
    return {
        "subject": email_message.subject,
        "to": email_message.to,
        "from_email": email_message.from_email,
        "reply_to": email_message.reply_to,
        "cc": email_message.cc,
        "bcc": email_message.bcc,
        # FIXME: "headers": email_message.headers,
        "body": email_message.body,
    }


def _deserializeEmailMessage(serialized_email_message):
    """
        Creates a "light" version of the original `EmailMessage` passed to the email backend.

        In order to be serializable, we:
        * only get the fields actually used by the app (defined in counterpart `_serializeEmailMessage`)
        * add a reference to the "synchronous" email backend (for convenience)

        *Tip*: use non-serializable objects only when deserialization is over... (f.i. email backends)
    """
    return EmailMessage(connection=get_connection(backend=ASYNC_EMAIL_BACKEND), **serialized_email_message)


@task(retries=_NB_RETRIES, retry_delay=settings.SEND_EMAIL_DELAY_BETWEEN_RETRIES_IN_SECONDS)
def _async_send_messages(serializable_email_messages):
    """ Async email sending "delegate"

        This function sends emails with the backend defined in `ASYNC_EMAIL_BACKEND`
        and is triggerred by an email backend wrappper: `AsyncEmailBackend`.

        As it is decorated as a Huey task, all parameters must be serializable via Pickle.

        Huey stores some data via the broker persistance mechanism (Redis | in-memory | SQLite)
        for RPC/async/retry purposes.

        In order to send data to a remote broker and perform callback function call on the client,
        Huey must use a serialization mechanism to send "over the wire" (Pickle here).

        In this case for a `@task`, data sent by Huey are:
        * the function name (to use as a callback)
        * its call parameters (to make the call)

        The main parameter is a list of `EmailMessage` objects to be send.

        By design, an `EmailMessage` instance holds references to some non-serializable ressources:
        * a connection to the email backend (if not `None`)
        * inner locks for atomic/threadsafe operations
        * ...

        Making `EmailMessage` serializable is the purpose of `_serializeEmailMessage` and `_deserializeEmailMessage`.

        If there are many async tasks to be defined or for specific objects,
        it may be better to use a custom serializer.

        By design (see `BaseEmailBackend.send_messages`), this function must return
        the number of email correctly processed.
    """

    count = 0

    for email in serializable_email_messages:
        message = _deserializeEmailMessage(email)
        for sanitized_message in sanitize_mailjet_recipients(message):
            sanitized_message.send()
            count += 1

    # This part is processed by an external worker. Return count is irrelevant, so:
    return count


class AsyncEmailBackend(BaseEmailBackend):
    """ Custom async email backend wrapper

        Decorating a method with `@task` does not work (no static context).
        Only functions can be Huey tasks.

        This class:
        * wraps an email backend defined in `settings.ASYNC_EMAIL_BACKEND`
        * delegate the actual email sending to a function with *serializable* parameters

        See:
        * `base.py` section "Huey" for details on `ASYNC_EMAIL_BACKEND`
        * `_async_send_messages` for more on details on async/serialization concerns
    """

    def send_messages(self, email_messages):
        # Turn emails into something serializable
        if not email_messages:
            return

        emails = [_serializeEmailMessage(email) for email in email_messages]

        return _async_send_messages(emails)
