from django.db.models import Count, Prefetch, Q

from itou.companies.models import Company
from itou.institutions.models import Institution
from itou.prescribers.models import PrescriberOrganization
from itou.users.models import User
from itou.utils.command import BaseCommand
from itou.utils.emails import send_email_messages


class Command(BaseCommand):
    """
    Send an email reminder every 3 months asking admins of companies, organizations and institutions
    having more than 1 member to review members access and ensure that only authorized members have
    access to the organization data.
    """

    def handle(self, *args, **options):
        # Companies
        companies = (
            Company.objects.active()
            .prefetch_related(
                Prefetch(
                    "members",
                    queryset=User.objects.distinct().filter(
                        is_active=True,
                        companymembership__is_active=True,
                        companymembership__is_admin=True,
                    ),
                    to_attr="admin_members",
                )
            )
            .annotate(
                active_members_count=Count(
                    "members",
                    filter=Q(
                        companymembership__is_active=True,
                        companymembership__user__is_active=True,
                    ),
                )
            )
            .filter(active_members_count__gt=1)
            .order_by("pk")
        )
        send_email_messages(
            company.check_authorized_members_email() for company in companies.iterator(chunk_size=1000)
        )

        # Prescriber organizations
        organizations = (
            PrescriberOrganization.objects.all()
            .prefetch_related(
                Prefetch(
                    "members",
                    queryset=User.objects.distinct().filter(
                        is_active=True,
                        prescribermembership__is_active=True,
                        prescribermembership__is_admin=True,
                    ),
                    to_attr="admin_members",
                )
            )
            .annotate(
                active_members_count=Count(
                    "members",
                    filter=Q(
                        prescribermembership__is_active=True,
                        prescribermembership__user__is_active=True,
                    ),
                )
            )
            .filter(active_members_count__gt=1)
            .order_by("pk")
        )
        send_email_messages(
            organization.check_authorized_members_email() for organization in organizations.iterator(chunk_size=1000)
        )

        # Institutions
        institutions = (
            Institution.objects.all()
            .prefetch_related(
                Prefetch(
                    "members",
                    queryset=User.objects.distinct().filter(
                        is_active=True,
                        institutionmembership__is_active=True,
                        institutionmembership__is_admin=True,
                    ),
                    to_attr="admin_members",
                )
            )
            .annotate(
                active_members_count=Count(
                    "members",
                    filter=Q(
                        institutionmembership__is_active=True,
                        institutionmembership__user__is_active=True,
                    ),
                )
            )
            .filter(active_members_count__gt=1)
            .order_by("pk")
        )
        send_email_messages(
            institution.check_authorized_members_email() for institution in institutions.iterator(chunk_size=1000)
        )
