from django.contrib.auth.models import Permission
from django.urls import reverse
from django.utils import timezone
from pytest_django.asserts import assertContains, assertNotContains, assertRedirects

from itou.users.enums import UserKind
from itou.users.factories import ItouStaffFactory, JobSeekerFactory
from itou.users.models import IdentityProvider, User


def test_add_user(client):
    admin_user = ItouStaffFactory(is_superuser=True)
    client.force_login(admin_user)
    response = client.post(
        reverse("admin:users_user_add"),
        {
            "username": "foo",
            "password1": "hunter2",
            "password2": "hunter2",
            "kind": UserKind.JOB_SEEKER,
            "utils-pksupportremark-content_type-object_id-INITIAL_FORMS": "0",
            "utils-pksupportremark-content_type-object_id-TOTAL_FORMS": "0",
        },
    )
    user = User.objects.get(username="foo")
    assertRedirects(response, reverse("admin:users_user_change", kwargs={"object_id": user.pk}))
    assert user.kind == UserKind.JOB_SEEKER


def test_no_email_sent(client):
    user = JobSeekerFactory(identity_provider=IdentityProvider.INCLUSION_CONNECT)

    # Typical admin user.
    admin_user = ItouStaffFactory(is_superuser=True)
    client.force_login(admin_user)
    now = timezone.now()
    naive_now = timezone.make_naive(now)
    response = client.post(
        reverse("admin:users_user_change", kwargs={"object_id": user.pk}),
        {
            "date_joined_0": naive_now.date(),
            "date_joined_1": naive_now.time(),
            "last_checked_at_0": naive_now.date(),
            "last_checked_at_1": naive_now.time(),
            # email was set by SSO.
            "kind": UserKind.JOB_SEEKER,
            "emailaddress_set-INITIAL_FORMS": "0",
            "emailaddress_set-TOTAL_FORMS": "0",
            "eligibility_diagnoses-INITIAL_FORMS": "0",
            "eligibility_diagnoses-TOTAL_FORMS": "0",
            "geiq_eligibility_diagnoses-INITIAL_FORMS": "0",
            "geiq_eligibility_diagnoses-TOTAL_FORMS": "0",
            "approvals-INITIAL_FORMS": "0",
            "approvals-TOTAL_FORMS": "0",
            "job_applications-INITIAL_FORMS": "0",
            "job_applications-TOTAL_FORMS": "0",
            "utils-pksupportremark-content_type-object_id-INITIAL_FORMS": "0",
            "utils-pksupportremark-content_type-object_id-TOTAL_FORMS": "0",
            "_save": "Save",
        },
    )
    assertRedirects(response, reverse("admin:users_user_changelist"))
    user_refreshed = User.objects.get(pk=user.pk)
    assert user_refreshed.kind == UserKind.JOB_SEEKER
    assert user_refreshed.first_name == user.first_name
    assert user_refreshed.last_name == user.last_name
    assert user_refreshed.date_joined == now
    assert user_refreshed.last_checked_at == now
    assert user_refreshed.identity_provider == IdentityProvider.INCLUSION_CONNECT


def test_hijack_button(client):
    user = JobSeekerFactory()
    hijack_url = reverse("hijack:acquire")

    # Basic staff users don't have access to the button
    admin_user = ItouStaffFactory()
    perms = Permission.objects.filter(codename__in=("change_user", "view_user"))
    admin_user.user_permissions.add(*perms)
    client.force_login(admin_user)
    response = client.get(reverse("admin:users_user_change", kwargs={"object_id": user.pk}))
    assertNotContains(response, hijack_url)

    # Superusers (and those matching has_hijack_perm) can
    admin_user.is_superuser = True
    admin_user.save(update_fields=("is_superuser",))
    response = client.get(reverse("admin:users_user_change", kwargs={"object_id": user.pk}))
    assertContains(response, hijack_url)


def test_app_model_change_url(admin_client):
    user = JobSeekerFactory()
    # Check that the page does not crash
    response = admin_client.get(reverse("admin:users_user_change", kwargs={"object_id": user.pk}))
    assert response.status_code == 200
    response = admin_client.get(
        reverse("admin:users_jobseekerprofile_change", kwargs={"object_id": user.jobseeker_profile.pk})
    )
    assert response.status_code == 200
