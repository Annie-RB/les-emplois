from django.urls import reverse
from django.utils import timezone
from pytest_django.asserts import assertRedirects

from itou.users.factories import JobSeekerFactory
from itou.users.models import IdentityProvider, User


def test_no_email_sent(client):
    user = JobSeekerFactory(identity_provider=IdentityProvider.INCLUSION_CONNECT)

    # Typical admin user.
    admin_user = JobSeekerFactory(is_staff=True, is_superuser=True)
    client.force_login(admin_user)
    now = timezone.now()
    naive_now = timezone.make_naive(now)
    response = client.post(
        reverse("admin:users_user_change", kwargs={"object_id": user.pk}),
        {
            "date_joined_0": naive_now.date(),
            "date_joined_1": naive_now.time(),
            # email was set by SSO.
            "is_job_seeker": True,
            "is_staff": True,
            "siaemembership_set-INITIAL_FORMS": "0",
            "siaemembership_set-TOTAL_FORMS": "0",
            "prescribermembership_set-INITIAL_FORMS": "0",
            "prescribermembership_set-TOTAL_FORMS": "0",
            "institutionmembership_set-INITIAL_FORMS": "0",
            "institutionmembership_set-TOTAL_FORMS": "0",
            "utils-pksupportremark-content_type-object_id-INITIAL_FORMS": "0",
            "utils-pksupportremark-content_type-object_id-TOTAL_FORMS": "0",
            "_save": "Save",
        },
    )
    assertRedirects(response, reverse("admin:users_user_changelist"))
    user_refreshed = User.objects.get(pk=user.pk)
    assert user_refreshed.is_staff is True
    assert user_refreshed.is_job_seeker is True
    assert user_refreshed.first_name == user.first_name
    assert user_refreshed.last_name == user.last_name
    assert user_refreshed.date_joined == now
    assert user_refreshed.identity_provider == IdentityProvider.INCLUSION_CONNECT
