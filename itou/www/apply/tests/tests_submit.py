import datetime
import uuid
from unittest import mock

import django.core.exceptions
import faker
from dateutil.relativedelta import relativedelta
from django.test import TestCase
from django.urls import resolve, reverse
from django.utils import timezone

from itou.approvals.factories import ApprovalFactory, PoleEmploiApprovalFactory
from itou.asp.models import RSAAllocation
from itou.cities.factories import create_test_cities
from itou.cities.models import City
from itou.eligibility.models import EligibilityDiagnosis
from itou.institutions.factories import InstitutionWithMembershipFactory
from itou.job_applications.enums import SenderKind
from itou.job_applications.models import JobApplication
from itou.prescribers.factories import PrescriberOrganizationWithMembershipFactory
from itou.siaes.enums import SiaeKind
from itou.siaes.factories import SiaeFactory, SiaeWithMembershipAndJobsFactory
from itou.users.factories import (
    DEFAULT_PASSWORD,
    JobSeekerFactory,
    JobSeekerProfileFactory,
    PrescriberFactory,
    UserFactory,
)
from itou.users.models import User
from itou.utils.storage.s3 import S3Upload


fake = faker.Faker(locale="fr_FR")


class ApplyTest(TestCase):
    def test_we_redirect_to_siae_on_missing_session_for_fbv(self):
        routes = {
            "apply:step_eligibility",
            "apply:step_application",
        }
        user = JobSeekerFactory()
        siae = SiaeFactory(with_jobs=True)

        self.client.login(username=user.email, password=DEFAULT_PASSWORD)
        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(reverse(route, kwargs={"siae_pk": siae.pk}))
                self.assertRedirects(response, reverse("siaes_views:card", kwargs={"siae_id": siae.pk}))

    def test_we_raise_a_permission_denied_on_missing_session_for_cbv(self):
        routes = {
            "apply:check_nir_for_sender",
            "apply:check_email_for_sender",
            "apply:check_nir_for_job_seeker",
            "apply:step_check_job_seeker_info",
            "apply:step_check_prev_applications",
            "apply:step_application_sent",
        }
        user = JobSeekerFactory()
        siae = SiaeFactory(with_jobs=True)

        self.client.login(username=user.email, password=DEFAULT_PASSWORD)
        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(reverse(route, kwargs={"siae_pk": siae.pk}))
                self.assertEqual(response.status_code, 403)
                self.assertEqual(response.context["exception"], "A session namespace doesn't exist.")

    def test_we_raise_a_permission_denied_on_missing_temporary_session_for_create_job_seeker(self):
        routes = {
            "apply:create_job_seeker_step_1_for_sender",
            "apply:create_job_seeker_step_2_for_sender",
            "apply:create_job_seeker_step_3_for_sender",
            "apply:create_job_seeker_step_end_for_sender",
        }
        user = JobSeekerFactory()
        siae = SiaeFactory(with_jobs=True)

        self.client.login(username=user.email, password=DEFAULT_PASSWORD)
        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(reverse(route, kwargs={"siae_pk": siae.pk, "session_uuid": uuid.uuid4()}))
                self.assertEqual(response.status_code, 403)
                self.assertEqual(response.context["exception"], "A session namespace doesn't exist.")


class ApplyAsJobSeekerTest(TestCase):
    @property
    def default_session_data(self):
        return {
            "back_url": None,
            "job_seeker_pk": None,
            "job_seeker_email": None,
            "nir": None,
            "siae_pk": None,
            "sender_pk": None,
            "sender_kind": None,
            "sender_siae_pk": None,
            "sender_prescriber_organization_pk": None,
            "job_description_id": None,
        }

    def test_apply_as_jobseeker(self):
        """Apply as jobseeker."""

        siae = SiaeWithMembershipAndJobsFactory(romes=("N1101", "N1105"))

        user = JobSeekerFactory(birthdate=None, nir="")
        self.client.login(username=user.email, password=DEFAULT_PASSWORD)

        # Entry point.
        # ----------------------------------------------------------------------

        url = reverse("apply:start", kwargs={"siae_pk": siae.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        session_data = self.client.session[f"job_application-{siae.pk}"]
        expected_session_data = self.default_session_data | {
            "job_seeker_pk": user.pk,
            "siae_pk": siae.pk,
            "sender_pk": user.pk,
            "sender_kind": SenderKind.JOB_SEEKER,
        }
        self.assertDictEqual(session_data, expected_session_data)

        next_url = reverse("apply:check_nir_for_job_seeker", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step check job seeker NIR.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        nir = "141068078200557"
        post_data = {"nir": nir, "confirm": 1}

        response = self.client.post(next_url, data=post_data)
        self.assertEqual(response.status_code, 302)

        user = User.objects.get(pk=user.pk)
        self.assertEqual(user.nir, nir)

        session_data = self.client.session[f"job_application-{siae.pk}"]
        expected_session_data = self.default_session_data | {
            "job_seeker_pk": user.pk,
            "siae_pk": siae.pk,
            "sender_pk": user.pk,
            "sender_kind": SenderKind.JOB_SEEKER,
        }
        self.assertDictEqual(session_data, expected_session_data)

        next_url = reverse("apply:step_check_job_seeker_info", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step check job seeker info.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        post_data = {"birthdate": "20/12/1978", "phone": "0610203040", "pole_emploi_id": "1234567A"}

        response = self.client.post(next_url, data=post_data)
        self.assertEqual(response.status_code, 302)

        user = User.objects.get(pk=user.pk)
        self.assertEqual(user.birthdate.strftime("%d/%m/%Y"), post_data["birthdate"])
        self.assertEqual(user.phone, post_data["phone"])

        self.assertEqual(user.pole_emploi_id, post_data["pole_emploi_id"])

        next_url = reverse("apply:step_check_prev_applications", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step check previous job applications.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 302)

        next_url = reverse("apply:step_eligibility", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step eligibility.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 302)

        next_url = reverse("apply:step_application", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step application.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        # Test fields mandatory to upload to S3
        s3_upload = S3Upload(kind="resume")

        # Don't test S3 form fields as it led to flaky tests and
        # it's already done by the Boto library.
        self.assertContains(response, s3_upload.form_values["url"])

        # Config variables
        s3_upload.config.pop("upload_expiration")
        for _, value in s3_upload.config.items():
            self.assertContains(response, value)

        post_data = {
            "selected_jobs": [siae.job_description_through.first().pk],
            "message": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "resume_link": "https://server.com/rocky-balboa.pdf",
        }
        response = self.client.post(next_url, data=post_data)
        self.assertEqual(response.status_code, 302)

        next_url = reverse("apply:step_application_sent", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        job_application = JobApplication.objects.get(job_seeker=user, sender=user, to_siae=siae)
        self.assertEqual(job_application.sender_kind, SenderKind.JOB_SEEKER)
        self.assertEqual(job_application.sender_siae, None)
        self.assertEqual(job_application.sender_prescriber_organization, None)
        self.assertEqual(job_application.state, job_application.state.workflow.STATE_NEW)
        self.assertEqual(job_application.message, post_data["message"])
        self.assertEqual(job_application.answer, "")
        self.assertEqual(job_application.selected_jobs.count(), 1)
        self.assertEqual(job_application.selected_jobs.first().pk, post_data["selected_jobs"][0])
        self.assertEqual(job_application.resume_link, post_data["resume_link"])

        self.client.get(next_url)
        self.assertNotIn(f"job_application-{siae.pk}", self.client.session)

    def test_apply_as_job_seeker_temporary_nir(self):
        """
        Full path is tested above. See test_apply_as_job_seeker.
        """
        siae = SiaeWithMembershipAndJobsFactory(romes=("N1101", "N1105"))

        user = JobSeekerFactory(nir="")
        self.client.login(username=user.email, password=DEFAULT_PASSWORD)

        # Entry point.
        # ----------------------------------------------------------------------

        url = reverse("apply:start", kwargs={"siae_pk": siae.pk})
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)
        next_url = reverse("apply:check_nir_for_job_seeker", kwargs={"siae_pk": siae.pk})

        # Follow all redirections until NIR.
        # ----------------------------------------------------------------------
        nir = "123456789KLOIU"
        post_data = {"nir": nir}

        response = self.client.post(next_url, data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())

        # Temporary number should be skipped.
        post_data = {"nir": nir, "skip": 1}
        response = self.client.post(next_url, data=post_data, follow=True)
        last_url = response.redirect_chain[-1][0]
        expected_url = reverse("apply:step_application", kwargs={"siae_pk": siae.pk})
        self.assertEqual(last_url, expected_url)
        self.assertEqual(response.status_code, 200)

        # Step application.
        # ----------------------------------------------------------------------

        response = self.client.get(last_url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            "selected_jobs": [siae.job_description_through.first().pk],
            "message": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "resume_link": "https://server.com/rocky-balboa.pdf",
        }
        response = self.client.post(last_url, data=post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        last_url = response.redirect_chain[-1][0]
        next_url = reverse("apply:step_application_sent", kwargs={"siae_pk": siae.pk})
        self.assertEqual(last_url, next_url)
        self.assertNotIn(f"job_application-{siae.pk}", self.client.session)
        user.refresh_from_db()
        self.assertFalse(user.nir)

    def test_apply_as_jobseeker_to_siae_with_approval_in_waiting_period(self):
        """
        Apply as jobseeker to a SIAE (not a GEIQ) with an approval in waiting period.
        Waiting period cannot be bypassed.
        """
        now_date = timezone.now().date() - relativedelta(months=1)
        now = timezone.datetime(year=now_date.year, month=now_date.month, day=now_date.day, tzinfo=timezone.utc)

        with mock.patch("django.utils.timezone.now", side_effect=lambda: now):
            siae = SiaeWithMembershipAndJobsFactory(romes=("N1101", "N1105"))
            user = JobSeekerFactory()
            end_at = now_date - relativedelta(days=30)
            start_at = end_at - relativedelta(years=2)
            PoleEmploiApprovalFactory(
                pole_emploi_id=user.pole_emploi_id, birthdate=user.birthdate, start_at=start_at, end_at=end_at
            )
            self.client.login(username=user.email, password=DEFAULT_PASSWORD)

            url = reverse("apply:start", kwargs={"siae_pk": siae.pk})

            # Follow all redirections…
            response = self.client.get(url, follow=True)

            # …until the expected 403.
            self.assertEqual(response.status_code, 403)
            self.assertIn("Vous avez terminé un parcours", response.context["exception"])
            last_url = response.redirect_chain[-1][0]
            self.assertEqual(last_url, reverse("apply:step_check_job_seeker_info", kwargs={"siae_pk": siae.pk}))

    def test_apply_as_job_seeker_on_sender_tunnel(self):
        siae = SiaeFactory()
        user = JobSeekerFactory()
        self.client.login(username=user.email, password=DEFAULT_PASSWORD)

        # Without a session namespace
        response = self.client.get(reverse("apply:check_nir_for_sender", kwargs={"siae_pk": siae.pk}))
        self.assertEqual(response.status_code, 403)

        # With a session namespace
        self.client.get(reverse("apply:start", kwargs={"siae_pk": siae.pk}))  # Use that view to init the session
        response = self.client.get(reverse("apply:check_nir_for_sender", kwargs={"siae_pk": siae.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("apply:start", kwargs={"siae_pk": siae.pk}))


class ApplyAsAuthorizedPrescriberTest(TestCase):
    def setUp(self):
        create_test_cities(["67"], num_per_department=1)
        self.city = City.objects.first()

    @property
    def default_session_data(self):
        return {
            "back_url": None,
            "job_seeker_pk": None,
            "job_seeker_email": None,
            "nir": None,
            "siae_pk": None,
            "sender_pk": None,
            "sender_kind": None,
            "sender_siae_pk": None,
            "sender_prescriber_organization_pk": None,
            "job_description_id": None,
        }

    def test_apply_as_prescriber_with_pending_authorization(self):
        """Apply as prescriber that has pending authorization."""

        siae = SiaeWithMembershipAndJobsFactory(romes=("N1101", "N1105"))

        prescriber_organization = PrescriberOrganizationWithMembershipFactory(with_pending_authorization=True)
        user = prescriber_organization.members.first()
        self.client.login(username=user.email, password=DEFAULT_PASSWORD)

        dummy_job_seeker_profile = JobSeekerProfileFactory.build()

        # Entry point.
        # ----------------------------------------------------------------------

        url = reverse("apply:start", kwargs={"siae_pk": siae.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        session = self.client.session
        session_data = session[f"job_application-{siae.pk}"]
        expected_session_data = self.default_session_data | {
            "siae_pk": siae.pk,
            "sender_pk": user.pk,
            "sender_kind": SenderKind.PRESCRIBER,
            "sender_prescriber_organization_pk": prescriber_organization.pk,
        }
        self.assertDictEqual(session_data, expected_session_data)

        next_url = reverse("apply:pending_authorization_for_sender", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step show warning message about pending authorization.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        next_url = reverse("apply:check_nir_for_sender", kwargs={"siae_pk": siae.pk})
        self.assertContains(response, "Status de prescripteur habilité non vérifié")
        self.assertContains(response, next_url)

        # Step determine the job seeker with a NIR.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(next_url, data={"nir": dummy_job_seeker_profile.user.nir, "confirm": 1})
        self.assertEqual(response.status_code, 302)
        session = self.client.session
        expected_session_data = self.default_session_data | {
            "nir": dummy_job_seeker_profile.user.nir,
            "siae_pk": siae.pk,
            "sender_pk": user.pk,
            "sender_kind": SenderKind.PRESCRIBER,
            "sender_prescriber_organization_pk": prescriber_organization.pk,
        }
        self.assertDictEqual(self.client.session[f"job_application-{siae.pk}"], expected_session_data)

        next_url = reverse("apply:check_email_for_sender", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step get job seeker e-mail.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(next_url, data={"email": dummy_job_seeker_profile.user.email, "confirm": "1"})
        self.assertEqual(response.status_code, 302)
        job_seeker_session_name = str(resolve(response.url).kwargs["session_uuid"])

        expected_job_seeker_session = {
            "user": {
                "email": dummy_job_seeker_profile.user.email,
                "nir": dummy_job_seeker_profile.user.nir,
            }
        }
        self.assertEqual(self.client.session[job_seeker_session_name], expected_job_seeker_session)

        next_url = reverse(
            "apply:create_job_seeker_step_1_for_sender",
            kwargs={"siae_pk": siae.pk, "session_uuid": job_seeker_session_name},
        )
        self.assertEqual(response.url, next_url)

        # Step create a job seeker.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            "title": dummy_job_seeker_profile.user.title,
            "first_name": dummy_job_seeker_profile.user.first_name,
            "last_name": dummy_job_seeker_profile.user.last_name,
            "birthdate": dummy_job_seeker_profile.user.birthdate,
        }
        response = self.client.post(next_url, data=post_data)
        self.assertEqual(response.status_code, 302)
        expected_job_seeker_session["user"] |= post_data
        self.assertEqual(self.client.session[job_seeker_session_name], expected_job_seeker_session)

        next_url = reverse(
            "apply:create_job_seeker_step_2_for_sender",
            kwargs={"siae_pk": siae.pk, "session_uuid": job_seeker_session_name},
        )
        self.assertEqual(response.url, next_url)

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            "address_line_1": dummy_job_seeker_profile.user.address_line_1,
            "post_code": self.city.post_codes[0],
            "city_slug": self.city.slug,
            "city": self.city.name,
            "phone": dummy_job_seeker_profile.user.phone,
        }
        response = self.client.post(next_url, data=post_data)
        self.assertEqual(response.status_code, 302)
        expected_job_seeker_session["user"] |= post_data | {"department": "67", "address_line_2": ""}
        self.assertEqual(self.client.session[job_seeker_session_name], expected_job_seeker_session)

        next_url = reverse(
            "apply:create_job_seeker_step_3_for_sender",
            kwargs={"siae_pk": siae.pk, "session_uuid": job_seeker_session_name},
        )
        self.assertEqual(response.url, next_url)

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            "education_level": dummy_job_seeker_profile.education_level,
        }
        response = self.client.post(next_url, data=post_data)
        self.assertEqual(response.status_code, 302)
        expected_job_seeker_session["profile"] = post_data | {
            "resourceless": False,
            "rqth_employee": False,
            "oeth_employee": False,
            "pole_emploi": False,
            "pole_emploi_id_forgotten": "",
            "pole_emploi_since": "",
            "unemployed": False,
            "unemployed_since": "",
            "rsa_allocation": False,
            "has_rsa_allocation": RSAAllocation.NO.value,
            "rsa_allocation_since": "",
            "ass_allocation": False,
            "ass_allocation_since": "",
            "aah_allocation": False,
            "aah_allocation_since": "",
        }
        expected_job_seeker_session["user"] |= {
            "pole_emploi_id": "",
            "lack_of_pole_emploi_id_reason": User.REASON_NOT_REGISTERED,
        }
        self.assertEqual(self.client.session[job_seeker_session_name], expected_job_seeker_session)

        next_url = reverse(
            "apply:create_job_seeker_step_end_for_sender",
            kwargs={"siae_pk": siae.pk, "session_uuid": job_seeker_session_name},
        )
        self.assertEqual(response.url, next_url)

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(next_url)
        self.assertEqual(response.status_code, 302)

        self.assertNotIn(job_seeker_session_name, self.client.session)
        new_job_seeker = User.objects.get(email=dummy_job_seeker_profile.user.email)
        expected_session_data = self.default_session_data | {
            "nir": dummy_job_seeker_profile.user.nir,
            "job_seeker_pk": new_job_seeker.pk,
            "siae_pk": siae.pk,
            "sender_pk": user.pk,
            "sender_kind": SenderKind.PRESCRIBER,
            "sender_prescriber_organization_pk": prescriber_organization.pk,
        }
        self.assertEqual(self.client.session[f"job_application-{siae.pk}"], expected_session_data)

        next_url = reverse("apply:step_eligibility", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step eligibility. Prescriber is not authorized yet.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 302)

        next_url = reverse("apply:step_application", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step application.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            "selected_jobs": [siae.job_description_through.first().pk, siae.job_description_through.last().pk],
            "message": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "resume_link": "https://server.com/rockie-balboa.pdf",
        }
        response = self.client.post(next_url, data=post_data)
        self.assertEqual(response.status_code, 302)

        next_url = reverse("apply:step_application_sent", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        job_application = JobApplication.objects.get(job_seeker=new_job_seeker, sender=user, to_siae=siae)
        self.assertEqual(job_application.sender_kind, SenderKind.PRESCRIBER)
        self.assertEqual(job_application.sender_siae, None)
        self.assertEqual(job_application.sender_prescriber_organization, prescriber_organization)
        self.assertEqual(job_application.state, job_application.state.workflow.STATE_NEW)
        self.assertEqual(job_application.message, post_data["message"])
        self.assertEqual(job_application.answer, "")
        self.assertEqual(job_application.selected_jobs.count(), 2)
        self.assertEqual(job_application.selected_jobs.first().pk, post_data["selected_jobs"][0])
        self.assertEqual(job_application.selected_jobs.last().pk, post_data["selected_jobs"][1])
        self.assertEqual(job_application.resume_link, post_data["resume_link"])

    def test_apply_as_authorized_prescriber(self):
        """Apply as authorized prescriber."""

        siae = SiaeWithMembershipAndJobsFactory(romes=("N1101", "N1105"))

        prescriber_organization = PrescriberOrganizationWithMembershipFactory(authorized=True)
        user = prescriber_organization.members.first()
        self.client.login(username=user.email, password=DEFAULT_PASSWORD)

        dummy_job_seeker_profile = JobSeekerProfileFactory.build()

        # Entry point.
        # ----------------------------------------------------------------------

        url = reverse("apply:start", kwargs={"siae_pk": siae.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        session_data = self.client.session[f"job_application-{siae.pk}"]
        expected_session_data = self.default_session_data | {
            "siae_pk": siae.pk,
            "sender_pk": user.pk,
            "sender_kind": SenderKind.PRESCRIBER,
            "sender_prescriber_organization_pk": prescriber_organization.pk,
        }
        self.assertDictEqual(session_data, expected_session_data)

        next_url = reverse("apply:check_nir_for_sender", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step determine the job seeker with a NIR.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(next_url, data={"nir": dummy_job_seeker_profile.user.nir, "confirm": 1})
        self.assertEqual(response.status_code, 302)
        expected_session_data = self.default_session_data | {
            "nir": dummy_job_seeker_profile.user.nir,
            "siae_pk": siae.pk,
            "sender_pk": user.pk,
            "sender_kind": SenderKind.PRESCRIBER,
            "sender_prescriber_organization_pk": prescriber_organization.pk,
        }
        self.assertDictEqual(self.client.session[f"job_application-{siae.pk}"], expected_session_data)

        next_url = reverse("apply:check_email_for_sender", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step get job seeker e-mail.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(next_url, data={"email": dummy_job_seeker_profile.user.email, "confirm": "1"})
        self.assertEqual(response.status_code, 302)
        job_seeker_session_name = str(resolve(response.url).kwargs["session_uuid"])

        expected_job_seeker_session = {
            "user": {
                "email": dummy_job_seeker_profile.user.email,
                "nir": dummy_job_seeker_profile.user.nir,
            }
        }
        self.assertEqual(self.client.session[job_seeker_session_name], expected_job_seeker_session)

        next_url = reverse(
            "apply:create_job_seeker_step_1_for_sender",
            kwargs={"siae_pk": siae.pk, "session_uuid": job_seeker_session_name},
        )
        self.assertEqual(response.url, next_url)

        # Step create a job seeker.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            "title": dummy_job_seeker_profile.user.title,
            "first_name": dummy_job_seeker_profile.user.first_name,
            "last_name": dummy_job_seeker_profile.user.last_name,
            "birthdate": dummy_job_seeker_profile.user.birthdate,
        }
        response = self.client.post(next_url, data=post_data)
        self.assertEqual(response.status_code, 302)
        expected_job_seeker_session["user"] |= post_data
        self.assertEqual(self.client.session[job_seeker_session_name], expected_job_seeker_session)

        next_url = reverse(
            "apply:create_job_seeker_step_2_for_sender",
            kwargs={"siae_pk": siae.pk, "session_uuid": job_seeker_session_name},
        )
        self.assertEqual(response.url, next_url)

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            "address_line_1": dummy_job_seeker_profile.user.address_line_1,
            "post_code": self.city.post_codes[0],
            "city_slug": self.city.slug,
            "city": self.city.name,
            "phone": dummy_job_seeker_profile.user.phone,
        }
        response = self.client.post(next_url, data=post_data)
        self.assertEqual(response.status_code, 302)
        expected_job_seeker_session["user"] |= post_data | {"department": "67", "address_line_2": ""}
        self.assertEqual(self.client.session[job_seeker_session_name], expected_job_seeker_session)

        next_url = reverse(
            "apply:create_job_seeker_step_3_for_sender",
            kwargs={"siae_pk": siae.pk, "session_uuid": job_seeker_session_name},
        )
        self.assertEqual(response.url, next_url)

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            "education_level": dummy_job_seeker_profile.education_level,
        }
        response = self.client.post(next_url, data=post_data)
        self.assertEqual(response.status_code, 302)
        expected_job_seeker_session["profile"] = post_data | {
            "resourceless": False,
            "rqth_employee": False,
            "oeth_employee": False,
            "pole_emploi": False,
            "pole_emploi_id_forgotten": "",
            "pole_emploi_since": "",
            "unemployed": False,
            "unemployed_since": "",
            "rsa_allocation": False,
            "has_rsa_allocation": RSAAllocation.NO.value,
            "rsa_allocation_since": "",
            "ass_allocation": False,
            "ass_allocation_since": "",
            "aah_allocation": False,
            "aah_allocation_since": "",
        }
        expected_job_seeker_session["user"] |= {
            "pole_emploi_id": "",
            "lack_of_pole_emploi_id_reason": User.REASON_NOT_REGISTERED,
        }
        self.assertEqual(self.client.session[job_seeker_session_name], expected_job_seeker_session)

        next_url = reverse(
            "apply:create_job_seeker_step_end_for_sender",
            kwargs={"siae_pk": siae.pk, "session_uuid": job_seeker_session_name},
        )
        self.assertEqual(response.url, next_url)

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(next_url)
        self.assertEqual(response.status_code, 302)

        self.assertNotIn(job_seeker_session_name, self.client.session)
        new_job_seeker = User.objects.get(email=dummy_job_seeker_profile.user.email)
        expected_session_data = self.default_session_data | {
            "nir": dummy_job_seeker_profile.user.nir,
            "job_seeker_pk": new_job_seeker.pk,
            "siae_pk": siae.pk,
            "sender_pk": user.pk,
            "sender_kind": SenderKind.PRESCRIBER,
            "sender_prescriber_organization_pk": prescriber_organization.pk,
        }
        self.assertEqual(self.client.session[f"job_application-{siae.pk}"], expected_session_data)

        next_url = reverse("apply:step_eligibility", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step eligibility.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        self.assertFalse(EligibilityDiagnosis.objects.has_considered_valid(new_job_seeker, for_siae=siae))

        response = self.client.post(next_url)
        self.assertEqual(response.status_code, 302)

        self.assertTrue(EligibilityDiagnosis.objects.has_considered_valid(new_job_seeker, for_siae=siae))

        next_url = reverse("apply:step_application", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step application.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            "selected_jobs": [siae.job_description_through.first().pk, siae.job_description_through.last().pk],
            "message": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "resume_link": "https://server.com/rockie-balboa.pdf",
        }
        response = self.client.post(next_url, data=post_data)
        self.assertEqual(response.status_code, 302)

        next_url = reverse("apply:step_application_sent", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        job_application = JobApplication.objects.get(job_seeker=new_job_seeker, sender=user, to_siae=siae)
        self.assertEqual(job_application.sender_kind, SenderKind.PRESCRIBER)
        self.assertEqual(job_application.sender_siae, None)
        self.assertEqual(job_application.sender_prescriber_organization, prescriber_organization)
        self.assertEqual(job_application.state, job_application.state.workflow.STATE_NEW)
        self.assertEqual(job_application.message, post_data["message"])
        self.assertEqual(job_application.answer, "")
        self.assertEqual(job_application.selected_jobs.count(), 2)
        self.assertEqual(job_application.selected_jobs.first().pk, post_data["selected_jobs"][0])
        self.assertEqual(job_application.selected_jobs.last().pk, post_data["selected_jobs"][1])
        self.assertEqual(job_application.resume_link, post_data["resume_link"])

        self.client.get(next_url)
        self.assertNotIn(f"job_application-{siae.pk}", self.client.session)

    def test_apply_as_authorized_prescriber_to_siae_for_approval_in_waiting_period(self):
        """
        Apply as authorized prescriber to a SIAE for a job seeker with an approval in waiting period.
        Being an authorized prescriber bypasses the waiting period.
        """

        siae = SiaeWithMembershipAndJobsFactory(romes=("N1101", "N1105"))

        job_seeker = JobSeekerFactory()

        # Create an approval in waiting period.
        end_at = datetime.date.today() - relativedelta(days=30)
        start_at = end_at - relativedelta(years=2)
        ApprovalFactory(user=job_seeker, start_at=start_at, end_at=end_at)

        prescriber_organization = PrescriberOrganizationWithMembershipFactory(authorized=True)
        user = prescriber_organization.members.first()
        self.client.login(username=user.email, password=DEFAULT_PASSWORD)

        url = reverse("apply:start", kwargs={"siae_pk": siae.pk})

        # Follow all redirections…
        response = self.client.get(url, follow=True)

        # …until a job seeker has to be determined…
        self.assertEqual(response.status_code, 200)
        last_url = response.redirect_chain[-1][0]
        self.assertEqual(last_url, reverse("apply:check_nir_for_sender", kwargs={"siae_pk": siae.pk}))

        # …choose one, then follow all redirections…
        post_data = {"nir": job_seeker.nir, "confirm": 1}
        response = self.client.post(last_url, data=post_data, follow=True)

        # …until the eligibility step which should trigger a 200 OK.
        self.assertEqual(response.status_code, 200)
        last_url = response.redirect_chain[-1][0]
        self.assertEqual(last_url, reverse("apply:step_eligibility", kwargs={"siae_pk": siae.pk}))

    def test_apply_to_a_geiq_as_authorized_prescriber(self):
        """Apply to a GEIQ as authorized prescriber."""

        siae = SiaeWithMembershipAndJobsFactory(kind=SiaeKind.GEIQ, romes=("N1101", "N1105"))

        prescriber_organization = PrescriberOrganizationWithMembershipFactory(authorized=True)
        user = prescriber_organization.members.first()
        self.client.login(username=user.email, password=DEFAULT_PASSWORD)
        job_seeker = JobSeekerFactory()

        # Entry point.
        # ----------------------------------------------------------------------

        url = reverse("apply:start", kwargs={"siae_pk": siae.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        session_data = self.client.session[f"job_application-{siae.pk}"]
        expected_session_data = self.default_session_data | {
            "siae_pk": siae.pk,
            "sender_pk": user.pk,
            "sender_kind": SenderKind.PRESCRIBER,
            "sender_prescriber_organization_pk": prescriber_organization.pk,
        }
        self.assertDictEqual(session_data, expected_session_data)

        next_url = reverse("apply:check_nir_for_sender", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step determine the job seeker.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        post_data = {"nir": job_seeker.nir, "confirm": 1}
        response = self.client.post(next_url, data=post_data)
        self.assertEqual(response.status_code, 302)

        next_url = reverse("apply:step_check_job_seeker_info", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step eligibility (not required when applying to a GEIQ).
        # ----------------------------------------------------------------------

        # Follow all redirections…
        response = self.client.get(next_url, follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertFalse(EligibilityDiagnosis.objects.has_considered_valid(job_seeker, for_siae=siae))

        # …until it hits the job application page.
        last_url = response.redirect_chain[-1][0]
        self.assertEqual(last_url, reverse("apply:step_application", kwargs={"siae_pk": siae.pk}))

        # Step application.
        # ----------------------------------------------------------------------

        response = self.client.get(last_url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            "selected_jobs": [siae.job_description_through.first().pk, siae.job_description_through.last().pk],
            "message": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "resume_link": "https://server.com/rockie-balboa.pdf",
        }
        response = self.client.post(last_url, data=post_data)
        self.assertEqual(response.status_code, 302)

        next_url = reverse("apply:step_application_sent", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        job_application = JobApplication.objects.get(job_seeker=job_seeker, sender=user, to_siae=siae)
        self.assertEqual(job_application.sender_kind, SenderKind.PRESCRIBER)
        self.assertEqual(job_application.sender_siae, None)
        self.assertEqual(job_application.sender_prescriber_organization, prescriber_organization)
        self.assertEqual(job_application.state, job_application.state.workflow.STATE_NEW)
        self.assertEqual(job_application.message, post_data["message"])
        self.assertEqual(job_application.answer, "")
        self.assertEqual(job_application.selected_jobs.count(), 2)
        self.assertEqual(job_application.selected_jobs.first().pk, post_data["selected_jobs"][0])
        self.assertEqual(job_application.selected_jobs.last().pk, post_data["selected_jobs"][1])
        self.assertEqual(job_application.resume_link, post_data["resume_link"])

        self.client.get(next_url)
        self.assertNotIn(f"job_application-{siae.pk}", self.client.session)


class ApplyAsPrescriberTest(TestCase):
    def setUp(self):
        create_test_cities(["67"], num_per_department=10)
        self.city = City.objects.first()

    @property
    def default_session_data(self):
        return {
            "back_url": None,
            "job_seeker_pk": None,
            "job_seeker_email": None,
            "nir": None,
            "siae_pk": None,
            "sender_pk": None,
            "sender_kind": None,
            "sender_siae_pk": None,
            "sender_prescriber_organization_pk": None,
            "job_description_id": None,
        }

    def test_apply_as_prescriber(self):
        siae = SiaeWithMembershipAndJobsFactory(romes=("N1101", "N1105"))

        user = PrescriberFactory()
        self.client.login(username=user.email, password=DEFAULT_PASSWORD)

        dummy_job_seeker_profile = JobSeekerProfileFactory.build()

        # Entry point.
        # ----------------------------------------------------------------------

        url = reverse("apply:start", kwargs={"siae_pk": siae.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        session_data = self.client.session[f"job_application-{siae.pk}"]
        expected_session_data = self.default_session_data | {
            "siae_pk": siae.pk,
            "sender_pk": user.pk,
            "sender_kind": SenderKind.PRESCRIBER,
        }
        self.assertDictEqual(session_data, expected_session_data)

        next_url = reverse("apply:check_nir_for_sender", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step determine the job seeker with a NIR.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(next_url, data={"nir": dummy_job_seeker_profile.user.nir, "confirm": 1})
        self.assertEqual(response.status_code, 302)

        expected_session_data = self.default_session_data | {
            "nir": dummy_job_seeker_profile.user.nir,
            "siae_pk": siae.pk,
            "sender_pk": user.pk,
            "sender_kind": SenderKind.PRESCRIBER,
        }
        self.assertDictEqual(self.client.session[f"job_application-{siae.pk}"], expected_session_data)

        next_url = reverse("apply:check_email_for_sender", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step get job seeker e-mail.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(next_url, data={"email": dummy_job_seeker_profile.user.email, "confirm": "1"})
        self.assertEqual(response.status_code, 302)
        job_seeker_session_name = str(resolve(response.url).kwargs["session_uuid"])

        expected_job_seeker_session = {
            "user": {
                "email": dummy_job_seeker_profile.user.email,
                "nir": dummy_job_seeker_profile.user.nir,
            }
        }
        self.assertEqual(self.client.session[job_seeker_session_name], expected_job_seeker_session)

        next_url = reverse(
            "apply:create_job_seeker_step_1_for_sender",
            kwargs={"siae_pk": siae.pk, "session_uuid": job_seeker_session_name},
        )
        self.assertEqual(response.url, next_url)

        # Step create a job seeker.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            "title": dummy_job_seeker_profile.user.title,
            "first_name": dummy_job_seeker_profile.user.first_name,
            "last_name": dummy_job_seeker_profile.user.last_name,
            "birthdate": dummy_job_seeker_profile.user.birthdate,
        }
        response = self.client.post(next_url, data=post_data)
        self.assertEqual(response.status_code, 302)
        expected_job_seeker_session["user"] |= post_data
        self.assertEqual(self.client.session[job_seeker_session_name], expected_job_seeker_session)

        next_url = reverse(
            "apply:create_job_seeker_step_2_for_sender",
            kwargs={"siae_pk": siae.pk, "session_uuid": job_seeker_session_name},
        )
        self.assertEqual(response.url, next_url)

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            "address_line_1": dummy_job_seeker_profile.user.address_line_1,
            "post_code": self.city.post_codes[0],
            "city_slug": self.city.slug,
            "city": self.city.name,
            "phone": dummy_job_seeker_profile.user.phone,
        }
        response = self.client.post(next_url, data=post_data)
        self.assertEqual(response.status_code, 302)
        expected_job_seeker_session["user"] |= post_data | {"department": "67", "address_line_2": ""}
        self.assertEqual(self.client.session[job_seeker_session_name], expected_job_seeker_session)

        next_url = reverse(
            "apply:create_job_seeker_step_3_for_sender",
            kwargs={"siae_pk": siae.pk, "session_uuid": job_seeker_session_name},
        )
        self.assertEqual(response.url, next_url)

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            "education_level": dummy_job_seeker_profile.education_level,
        }
        response = self.client.post(next_url, data=post_data)
        self.assertEqual(response.status_code, 302)
        expected_job_seeker_session["profile"] = post_data | {
            "resourceless": False,
            "rqth_employee": False,
            "oeth_employee": False,
            "pole_emploi": False,
            "pole_emploi_id_forgotten": "",
            "pole_emploi_since": "",
            "unemployed": False,
            "unemployed_since": "",
            "rsa_allocation": False,
            "has_rsa_allocation": RSAAllocation.NO.value,
            "rsa_allocation_since": "",
            "ass_allocation": False,
            "ass_allocation_since": "",
            "aah_allocation": False,
            "aah_allocation_since": "",
        }
        expected_job_seeker_session["user"] |= {
            "pole_emploi_id": "",
            "lack_of_pole_emploi_id_reason": User.REASON_NOT_REGISTERED,
        }
        self.assertEqual(self.client.session[job_seeker_session_name], expected_job_seeker_session)

        next_url = reverse(
            "apply:create_job_seeker_step_end_for_sender",
            kwargs={"siae_pk": siae.pk, "session_uuid": job_seeker_session_name},
        )
        self.assertEqual(response.url, next_url)

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        # Let's add another job seeker with exactly the same NIR, in the middle of the process.
        # ----------------------------------------------------------------------
        other_job_seeker = JobSeekerFactory(nir=dummy_job_seeker_profile.user.nir)

        expected_message = "Un objet Utilisateur avec ce champ NIR existe déjà."
        with self.assertRaisesMessage(django.core.exceptions.ValidationError, expected_message):
            response = self.client.post(next_url)
        self.assertTrue(response.status_code, 200)

        # Remove that extra job seeker and proceed with "normal" flow
        # ----------------------------------------------------------------------
        other_job_seeker.delete()

        response = self.client.post(next_url)
        self.assertEqual(response.status_code, 302)

        self.assertNotIn(job_seeker_session_name, self.client.session)
        new_job_seeker = User.objects.get(email=dummy_job_seeker_profile.user.email)
        expected_session_data = self.default_session_data | {
            "nir": dummy_job_seeker_profile.user.nir,
            "job_seeker_pk": new_job_seeker.pk,
            "siae_pk": siae.pk,
            "sender_pk": user.pk,
            "sender_kind": SenderKind.PRESCRIBER,
        }
        self.assertEqual(self.client.session[f"job_application-{siae.pk}"], expected_session_data)

        next_url = reverse("apply:step_eligibility", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step eligibility.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 302)

        next_url = reverse("apply:step_application", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step application.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            "selected_jobs": [siae.job_description_through.first().pk, siae.job_description_through.last().pk],
            "message": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "resume_link": "https://server.com/rockie-balboa.pdf",
        }
        response = self.client.post(next_url, data=post_data)
        self.assertEqual(response.status_code, 302)

        next_url = reverse("apply:step_application_sent", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        job_application = JobApplication.objects.get(job_seeker=new_job_seeker, sender=user, to_siae=siae)
        self.assertEqual(job_application.sender_kind, SenderKind.PRESCRIBER)
        self.assertEqual(job_application.sender_siae, None)
        self.assertEqual(job_application.sender_prescriber_organization, None)
        self.assertEqual(job_application.state, job_application.state.workflow.STATE_NEW)
        self.assertEqual(job_application.message, post_data["message"])
        self.assertEqual(job_application.answer, "")
        self.assertEqual(job_application.selected_jobs.count(), 2)
        self.assertEqual(job_application.selected_jobs.first().pk, post_data["selected_jobs"][0])
        self.assertEqual(job_application.selected_jobs.last().pk, post_data["selected_jobs"][1])
        self.assertEqual(job_application.resume_link, post_data["resume_link"])

        self.client.get(next_url)
        self.assertNotIn(f"job_application-{siae.pk}", self.client.session)

    def test_apply_as_prescriber_for_approval_in_waiting_period(self):
        """Apply as prescriber for a job seeker with an approval in waiting period."""

        siae = SiaeWithMembershipAndJobsFactory(romes=("N1101", "N1105"))

        job_seeker = JobSeekerFactory()

        # Create an approval in waiting period.
        end_at = datetime.date.today() - relativedelta(days=30)
        start_at = end_at - relativedelta(years=2)
        ApprovalFactory(user=job_seeker, start_at=start_at, end_at=end_at)

        user = PrescriberFactory()
        self.client.login(username=user.email, password=DEFAULT_PASSWORD)

        url = reverse("apply:start", kwargs={"siae_pk": siae.pk})

        # Follow all redirections…
        response = self.client.get(url, follow=True)

        # …until a job seeker has to be determined…
        self.assertEqual(response.status_code, 200)
        last_url = response.redirect_chain[-1][0]
        self.assertEqual(last_url, reverse("apply:check_nir_for_sender", kwargs={"siae_pk": siae.pk}))

        # …choose one, then follow all redirections…
        post_data = {"nir": job_seeker.nir, "confirm": 1}
        response = self.client.post(last_url, data=post_data, follow=True)

        # …until the expected 403.
        self.assertEqual(response.status_code, 403)
        self.assertIn("Le candidat a terminé un parcours", response.context["exception"])
        last_url = response.redirect_chain[-1][0]
        self.assertEqual(last_url, reverse("apply:step_check_job_seeker_info", kwargs={"siae_pk": siae.pk}))

    def test_apply_as_prescriber_on_job_seeker_tunnel(self):
        siae = SiaeFactory()
        user = PrescriberFactory()
        self.client.login(username=user.email, password=DEFAULT_PASSWORD)

        # Without a session namespace
        response = self.client.get(reverse("apply:check_nir_for_job_seeker", kwargs={"siae_pk": siae.pk}))
        self.assertEqual(response.status_code, 403)

        # With a session namespace
        self.client.get(reverse("apply:start", kwargs={"siae_pk": siae.pk}))  # Use that view to init the session
        response = self.client.get(reverse("apply:check_nir_for_job_seeker", kwargs={"siae_pk": siae.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("apply:start", kwargs={"siae_pk": siae.pk}))


class ApplyAsPrescriberNirExceptionsTest(TestCase):
    """
    The following normal use cases are tested in tests above:
        - job seeker creation,
        - job seeker found with a unique NIR.
    But, for historical reasons, our database is not perfectly clean.
    Some job seekers share the same NIR as the historical unique key was the e-mail address.
    Or the NIR is not found because their account was created before
    we added this possibility.
    """

    def create_test_data(self):
        siae = SiaeWithMembershipAndJobsFactory(romes=("N1101", "N1105"))
        # Only authorized prescribers can add a NIR.
        # See User.can_add_nir
        prescriber_organization = PrescriberOrganizationWithMembershipFactory(authorized=True)
        user = prescriber_organization.members.first()
        return siae, user

    def test_one_account_no_nir(self):
        """
        No account with this NIR is found.
        A search by email is proposed.
        An account is found for this email.
        This NIR account is empty.
        An update is expected.
        """
        job_seeker = JobSeekerFactory(nir="")
        # Create an approval to bypass the eligibility diagnosis step.
        PoleEmploiApprovalFactory(birthdate=job_seeker.birthdate, pole_emploi_id=job_seeker.pole_emploi_id)
        siae, user = self.create_test_data()
        self.client.login(username=user.email, password=DEFAULT_PASSWORD)

        url = reverse("apply:start", kwargs={"siae_pk": siae.pk})

        # Follow all redirections…
        response = self.client.get(url, follow=True)

        # …until a job seeker has to be determined.
        self.assertEqual(response.status_code, 200)
        last_url = response.redirect_chain[-1][0]
        self.assertEqual(last_url, reverse("apply:check_nir_for_sender", kwargs={"siae_pk": siae.pk}))

        # Enter a non-existing NIR.
        # ----------------------------------------------------------------------
        nir = "141068078200557"
        post_data = {"nir": nir, "confirm": 1}
        response = self.client.post(last_url, data=post_data)
        next_url = reverse("apply:check_email_for_sender", kwargs={"siae_pk": siae.pk})
        self.assertRedirects(response, next_url)

        # Create a job seeker with this NIR right after the check. Sorry.
        # ----------------------------------------------------------------------
        other_job_seeker = JobSeekerFactory(nir=nir)

        # Enter an existing email.
        # ----------------------------------------------------------------------
        post_data = {"email": job_seeker.email, "confirm": "1"}
        response = self.client.post(next_url, data=post_data)
        self.assertTrue(response.status_code, 200)
        self.assertIn(
            "Le<b> numéro de sécurité sociale</b> renseigné (141068078200557) "
            "est déjà utilisé par un autre candidat sur la Plateforme.",
            str(list(response.context["messages"])[0]),
        )

        # Remove that extra job seeker and proceed with "normal" flow
        # ----------------------------------------------------------------------
        other_job_seeker.delete()

        response = self.client.post(next_url, data=post_data)
        self.assertRedirects(
            response, reverse("apply:step_check_job_seeker_info", kwargs={"siae_pk": siae.pk}), target_status_code=302
        )

        response = self.client.post(next_url, data=post_data, follow=True)
        self.assertTrue(response.status_code, 200)
        self.assertEqual(0, len(list(response.context["messages"])))

        # Follow all redirections until the end.
        # ----------------------------------------------------------------------

        next_url = reverse("apply:step_application", kwargs={"siae_pk": siae.pk})
        post_data = {
            "selected_jobs": [siae.job_description_through.first().pk, siae.job_description_through.last().pk],
            "message": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "resume_link": "https://server.com/rockie-balboa.pdf",
        }
        response = self.client.post(next_url, data=post_data, follow=True)
        expected_url = reverse("apply:step_application_sent", kwargs={"siae_pk": siae.pk})
        last_url = response.redirect_chain[-1][0]
        self.assertEqual(expected_url, last_url)

        # Make sure the job seeker NIR is now filled in.
        # ----------------------------------------------------------------------
        job_seeker.refresh_from_db()
        self.assertEqual(job_seeker.nir, nir)


class ApplyAsSiaeTest(TestCase):
    def setUp(self):
        create_test_cities(["67"], num_per_department=1)
        self.city = City.objects.first()

    @property
    def default_session_data(self):
        return {
            "back_url": None,
            "job_seeker_pk": None,
            "job_seeker_email": None,
            "nir": None,
            "siae_pk": None,
            "sender_pk": None,
            "sender_kind": None,
            "sender_siae_pk": None,
            "sender_prescriber_organization_pk": None,
            "job_description_id": None,
        }

    def test_perms_for_siae(self):
        """An SIAE can postulate only for itself."""
        siae1 = SiaeFactory(with_membership=True)
        siae2 = SiaeFactory(with_membership=True)

        user = siae1.members.first()
        self.client.login(username=user.email, password=DEFAULT_PASSWORD)

        url = reverse("apply:start", kwargs={"siae_pk": siae2.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_apply_as_siae(self):
        """Apply as SIAE."""

        siae = SiaeWithMembershipAndJobsFactory(romes=("N1101", "N1105"))

        user = siae.members.first()
        self.client.login(username=user.email, password=DEFAULT_PASSWORD)

        dummy_job_seeker_profile = JobSeekerProfileFactory.build()

        # Entry point.
        # ----------------------------------------------------------------------

        url = reverse("apply:start", kwargs={"siae_pk": siae.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        session_data = self.client.session[f"job_application-{siae.pk}"]
        expected_session_data = self.default_session_data | {
            "siae_pk": siae.pk,
            "sender_pk": user.pk,
            "sender_kind": SenderKind.SIAE_STAFF,
            "sender_siae_pk": siae.pk,
        }
        self.assertDictEqual(session_data, expected_session_data)

        next_url = reverse("apply:check_nir_for_sender", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step determine the job seeker with a NIR.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(next_url, data={"nir": dummy_job_seeker_profile.user.nir, "confirm": 1})
        self.assertEqual(response.status_code, 302)

        expected_session_data = self.default_session_data | {
            "nir": dummy_job_seeker_profile.user.nir,
            "siae_pk": siae.pk,
            "sender_pk": user.pk,
            "sender_kind": SenderKind.SIAE_STAFF,
            "sender_siae_pk": siae.pk,
        }
        self.assertDictEqual(self.client.session[f"job_application-{siae.pk}"], expected_session_data)

        next_url = reverse("apply:check_email_for_sender", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step get job seeker e-mail.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(next_url, data={"email": dummy_job_seeker_profile.user.email, "confirm": "1"})
        self.assertEqual(response.status_code, 302)
        job_seeker_session_name = str(resolve(response.url).kwargs["session_uuid"])

        expected_job_seeker_session = {
            "user": {
                "email": dummy_job_seeker_profile.user.email,
                "nir": dummy_job_seeker_profile.user.nir,
            }
        }
        self.assertEqual(self.client.session[job_seeker_session_name], expected_job_seeker_session)

        next_url = reverse(
            "apply:create_job_seeker_step_1_for_sender",
            kwargs={"siae_pk": siae.pk, "session_uuid": job_seeker_session_name},
        )
        self.assertEqual(response.url, next_url)

        # Step create a job seeker.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            "title": dummy_job_seeker_profile.user.title,
            "first_name": dummy_job_seeker_profile.user.first_name,
            "last_name": dummy_job_seeker_profile.user.last_name,
            "birthdate": dummy_job_seeker_profile.user.birthdate,
        }
        response = self.client.post(next_url, data=post_data)
        self.assertEqual(response.status_code, 302)
        expected_job_seeker_session["user"] |= post_data
        self.assertEqual(self.client.session[job_seeker_session_name], expected_job_seeker_session)

        next_url = reverse(
            "apply:create_job_seeker_step_2_for_sender",
            kwargs={"siae_pk": siae.pk, "session_uuid": job_seeker_session_name},
        )
        self.assertEqual(response.url, next_url)

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            "address_line_1": dummy_job_seeker_profile.user.address_line_1,
            "post_code": self.city.post_codes[0],
            "city_slug": self.city.slug,
            "city": self.city.name,
            "phone": dummy_job_seeker_profile.user.phone,
        }
        response = self.client.post(next_url, data=post_data)
        self.assertEqual(response.status_code, 302)
        expected_job_seeker_session["user"] |= post_data | {"department": "67", "address_line_2": ""}
        self.assertEqual(self.client.session[job_seeker_session_name], expected_job_seeker_session)

        next_url = reverse(
            "apply:create_job_seeker_step_3_for_sender",
            kwargs={"siae_pk": siae.pk, "session_uuid": job_seeker_session_name},
        )
        self.assertEqual(response.url, next_url)

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            "education_level": dummy_job_seeker_profile.education_level,
        }
        response = self.client.post(next_url, data=post_data)
        self.assertEqual(response.status_code, 302)
        expected_job_seeker_session["profile"] = post_data | {
            "resourceless": False,
            "rqth_employee": False,
            "oeth_employee": False,
            "pole_emploi": False,
            "pole_emploi_id_forgotten": "",
            "pole_emploi_since": "",
            "unemployed": False,
            "unemployed_since": "",
            "rsa_allocation": False,
            "has_rsa_allocation": RSAAllocation.NO.value,
            "rsa_allocation_since": "",
            "ass_allocation": False,
            "ass_allocation_since": "",
            "aah_allocation": False,
            "aah_allocation_since": "",
        }
        expected_job_seeker_session["user"] |= {
            "pole_emploi_id": "",
            "lack_of_pole_emploi_id_reason": User.REASON_NOT_REGISTERED,
        }
        self.assertEqual(self.client.session[job_seeker_session_name], expected_job_seeker_session)

        next_url = reverse(
            "apply:create_job_seeker_step_end_for_sender",
            kwargs={"siae_pk": siae.pk, "session_uuid": job_seeker_session_name},
        )
        self.assertEqual(response.url, next_url)

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        response = self.client.post(next_url)
        self.assertEqual(response.status_code, 302)

        self.assertNotIn(job_seeker_session_name, self.client.session)
        new_job_seeker = User.objects.get(email=dummy_job_seeker_profile.user.email)
        expected_session_data = self.default_session_data | {
            "nir": dummy_job_seeker_profile.user.nir,
            "job_seeker_pk": new_job_seeker.pk,
            "siae_pk": siae.pk,
            "sender_pk": user.pk,
            "sender_kind": SenderKind.SIAE_STAFF,
            "sender_siae_pk": siae.pk,
        }
        self.assertEqual(self.client.session[f"job_application-{siae.pk}"], expected_session_data)

        next_url = reverse("apply:step_eligibility", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step eligibility.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 302)

        next_url = reverse("apply:step_application", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        # Step application.
        # ----------------------------------------------------------------------

        response = self.client.get(next_url)
        self.assertEqual(response.status_code, 200)

        post_data = {
            "selected_jobs": [siae.job_description_through.first().pk, siae.job_description_through.last().pk],
            "message": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "resume_link": "https://server.com/rockie-balboa.pdf",
        }
        response = self.client.post(next_url, data=post_data)
        self.assertEqual(response.status_code, 302)

        next_url = reverse("apply:step_application_sent", kwargs={"siae_pk": siae.pk})
        self.assertEqual(response.url, next_url)

        job_application = JobApplication.objects.get(job_seeker=new_job_seeker, sender=user, to_siae=siae)
        self.assertEqual(job_application.sender_kind, SenderKind.SIAE_STAFF)
        self.assertEqual(job_application.sender_siae, siae)
        self.assertEqual(job_application.sender_prescriber_organization, None)
        self.assertEqual(job_application.state, job_application.state.workflow.STATE_NEW)
        self.assertEqual(job_application.message, post_data["message"])
        self.assertEqual(job_application.answer, "")
        self.assertEqual(job_application.selected_jobs.count(), 2)
        self.assertEqual(job_application.selected_jobs.first().pk, post_data["selected_jobs"][0])
        self.assertEqual(job_application.selected_jobs.last().pk, post_data["selected_jobs"][1])
        self.assertEqual(job_application.resume_link, post_data["resume_link"])

        response = self.client.get(next_url)
        self.assertNotIn(f"job_application-{siae.pk}", self.client.session)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("apply:list_for_siae"))

    def test_apply_as_siae_for_approval_in_waiting_period(self):
        """Apply as SIAE for a job seeker with an approval in waiting period."""

        siae = SiaeWithMembershipAndJobsFactory(romes=("N1101", "N1105"))

        job_seeker = JobSeekerFactory()

        # Create an approval in waiting period.
        end_at = datetime.date.today() - relativedelta(days=30)
        start_at = end_at - relativedelta(years=2)
        ApprovalFactory(user=job_seeker, start_at=start_at, end_at=end_at)

        user = siae.members.first()
        self.client.login(username=user.email, password=DEFAULT_PASSWORD)

        url = reverse("apply:start", kwargs={"siae_pk": siae.pk})

        # Follow all redirections…
        response = self.client.get(url, follow=True)

        # …until a job seeker has to be determined…
        self.assertEqual(response.status_code, 200)
        last_url = response.redirect_chain[-1][0]
        self.assertEqual(last_url, reverse("apply:check_nir_for_sender", kwargs={"siae_pk": siae.pk}))

        # …choose one, then follow all redirections…
        post_data = {
            "nir": job_seeker.nir,
            "confirm": 1,
        }
        response = self.client.post(last_url, data=post_data, follow=True)

        # …until the expected 403.
        self.assertEqual(response.status_code, 403)
        self.assertIn("Le candidat a terminé un parcours", response.context["exception"])
        last_url = response.redirect_chain[-1][0]
        self.assertEqual(last_url, reverse("apply:step_check_job_seeker_info", kwargs={"siae_pk": siae.pk}))


class ApplyAsOtherTest(TestCase):
    ROUTES = [
        "apply:start",
        "apply:check_nir_for_job_seeker",
        "apply:check_nir_for_sender",
    ]

    def test_labor_inspectors_are_not_allowed_to_submit_application(self):
        siae = SiaeFactory()
        institution = InstitutionWithMembershipFactory()

        self.client.login(username=institution.members.first().email, password=DEFAULT_PASSWORD)

        for route in self.ROUTES:
            with self.subTest(route=route):
                response = self.client.get(reverse(route, kwargs={"siae_pk": siae.pk}), follow=True)
                self.assertEqual(response.status_code, 403)

    def test_an_account_without_rights_is_not_allowed_to_submit_application(self):
        siae = SiaeFactory()
        user = UserFactory(is_job_seeker=False, is_prescriber=False, is_siae_staff=False, is_labor_inspector=False)

        self.client.login(username=user.email, password=DEFAULT_PASSWORD)

        for route in self.ROUTES:
            with self.subTest(route=route):
                response = self.client.get(reverse(route, kwargs={"siae_pk": siae.pk}), follow=True)
                self.assertEqual(response.status_code, 403)
