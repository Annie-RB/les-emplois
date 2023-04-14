import importlib
import io
import os
import queue
import threading
from typing import NamedTuple

import httpx
import openpyxl
from bs4 import BeautifulSoup
from django.contrib.messages import DEFAULT_LEVELS, get_messages
from django.http import HttpResponse
from django.test import Client, TestCase as BaseTestCase
from django.test.utils import TestContextDecorator


# SAVEPOINT + RELEASE from the ATOMIC_REQUESTS transaction
BASE_NUM_QUERIES = 2


class Message(NamedTuple):
    level: int
    message: str


LEVEL_TO_NAME = {intlevel: name for name, intlevel in DEFAULT_LEVELS.items()}


def assertMessagesFromRequest(request, expected_messages: list[Message]):
    request_messages = get_messages(request)
    for message, (expected_level, expected_msg) in zip(request_messages, expected_messages, strict=True):
        msg_levelname = LEVEL_TO_NAME.get(message.level, message.level)
        expected_levelname = LEVEL_TO_NAME.get(expected_level, expected_level)
        assert (msg_levelname, message.message) == (expected_levelname, expected_msg)


def assertMessages(response: HttpResponse, expected_messages: list[Message]):
    assertMessagesFromRequest(response.wsgi_request, expected_messages)


class NuMessage:
    def __init__(self, message, content):
        self.content = content
        self.message_infos = message

    @property
    def message(self):
        return self.message_infos["message"]

    def extract(self, context: int | None = None):
        if context is None:
            return self.message_infos["extract"]
        last_line = self.message_infos["lastLine"]
        return "\n".join(self.content.decode().splitlines()[max(0, last_line - context) : last_line + context])


class NuValidationError(Exception):
    def __init__(self, messages, content):
        super().__init__(*sorted(set(msg["message"] for msg in messages)))
        self.content = content
        self.messages = [NuMessage(message, content) for message in messages]

    def debug(self, context=10):
        for message in self.messages:
            print("-" * 40)
            print(f"/!\\ {message.message}")
            print("-" * 40)
            print(message.extract(context))
            print()


class NuValidationClient:
    def __init__(self, url):
        self.url = url
        self.client = httpx.Client()
        self.work_queue = queue.Queue()
        self.source_to_messages = {}
        self.source_to_details = {}
        self.worker = None

        self.nb_validation = 0
        self.nb_validation_with_messages = 0

    def validate(self, source, content, partial=False):
        if self.worker is not None:
            self._add_work(source, content, partial)
            return
        messages = self._validate(source, content, partial)
        if messages:
            error = NuValidationError(messages, content)
            raise error

    def start_worker(self):
        if self.worker is None:
            self.worker = threading.Thread(target=self._work, daemon=True)
            self.worker.start()

    def _add_work(self, source, content, partial):
        self.work_queue.put((source, content, partial))

    def _work(self):
        while True:
            work = self.work_queue.get()
            [source, content, partial] = work
            self._validate(source, content, partial)
            self.work_queue.task_done()

    def _validate(self, source, content, partial):
        if partial:
            content = b'<!DOCTYPE html><html lang=""><head><title>Test</title></head><body>%b</body></html>' % content
        messages = self.client.post(
            self.url,
            params={
                "out": "json",
                "level": os.getenv("NU_VALIDATION_LEVEL", "error"),
                "filterpattern": (
                    ".*Attribute “hx-.*” not allowed on element “.*” at this point.|"
                    ".*Attribute “matomo-.*” not allowed on element “.*” at this point.|"
                    ".*Bad value “None” for attribute “lang” on element “select”.*|"  # https://github.com/codingjoe/django-select2/pull/206/files  # noqa: E501
                    "The value of the “for” attribute of the “label” element must be the ID of a non-hidden form control."  # duet-date-picker magic  # noqa: E501
                ),
            },
            content=content,
            headers={"Content-Type": "text/html;charset=utf-8"},
        ).json()["messages"]
        self.nb_validation += 1
        if messages:
            self.nb_validation_with_messages += 1
            self.source_to_messages.setdefault(source, set()).update(msg["message"] for msg in messages)
            self.source_to_details.setdefault(source, []).extend(messages)
        return messages


nu_validation_client = None
if nu_url := os.getenv("NU_VALIDATION_HOST"):
    nu_validation_client = NuValidationClient(nu_url)


def pprint_html(response, **selectors):
    """
    Pretty-print HTML responses (or fragment selected with :arg:`selector`)

    Heed the warning from
    https://www.crummy.com/software/BeautifulSoup/bs4/doc/#pretty-printing :

    > Since it adds whitespace (in the form of newlines), prettify() changes
      the meaning of an HTML document and should not be used to reformat one.
      The goal of prettify() is to help you visually understand the structure
      of the documents you work with.

    Use `snapshot`s, `assertHTMLEqual` and `assertContains(…, html=True)` to
    make assertions.
    """
    parser = BeautifulSoup(response.content, "html5lib")
    print("\n\n".join([elt.prettify() for elt in parser.find_all(**selectors)]))


def parse_response_to_soup(response, selector=None, no_html_body=False):
    soup = BeautifulSoup(response.content, "html5lib", from_encoding=response.charset or "utf-8")
    if no_html_body:
        # If the provided HTML does not contain <html><body> tags
        # html5lib will always add them around the response:
        # ignore them
        soup = soup.body
    if selector is not None:
        [soup] = soup.select(selector)
    for csrf_token_input in soup.find_all("input", attrs={"name": "csrfmiddlewaretoken"}):
        csrf_token_input["value"] = "NORMALIZED_CSRF_TOKEN"
    if "nonce" in soup.attrs:
        soup["nonce"] = "NORMALIZED_CSP_NONCE"
    for csp_nonce_script in soup.find_all("script", {"nonce": True}):
        csp_nonce_script["nonce"] = "NORMALIZED_CSP_NONCE"
    return soup


class NoInlineClient(Client):
    def request(self, **request):
        response = super().request(**request)
        content_type = response["Content-Type"].split(";")[0]
        if content_type == "text/html" and response.content:
            content = response.content.decode(response.charset)
            assert " onclick=" not in content
            assert " onbeforeinput=" not in content
            assert " onbeforeinput=" not in content
            assert " onchange=" not in content
            assert " oncopy=" not in content
            assert " oncut=" not in content
            assert " ondrag=" not in content
            assert " ondragend=" not in content
            assert " ondragenter=" not in content
            assert " ondragleave=" not in content
            assert " ondragover=" not in content
            assert " ondragstart=" not in content
            assert " ondrop=" not in content
            assert " oninput=" not in content
            assert "<script>" not in content
        if nu_validation_client is not None:
            if hasattr(response, "content") and response.content:
                # Basic heuristic to detect partial response
                partial = b"<html" not in response.content and b"<body" not in response.content
                nu_validation_client.validate(response.resolver_match.route, response.content, partial)

        return response


class TestCase(BaseTestCase):
    client_class = NoInlineClient


class reload_module(TestContextDecorator):
    def __init__(self, module):
        self._module = module
        self._original_values = {key: getattr(module, key) for key in dir(module) if not key.startswith("__")}
        super().__init__()

    def enable(self):
        importlib.reload(self._module)

    def disable(self):
        for key, value in self._original_values.items():
            setattr(self._module, key, value)


def get_rows_from_streaming_response(response):
    """Helper to read streamed XLSX files in tests"""

    content = b"".join(response.streaming_content)
    workbook = openpyxl.load_workbook(io.BytesIO(content))
    worksheet = workbook.active
    return [[cell.value or "" for cell in row] for row in worksheet.rows]
