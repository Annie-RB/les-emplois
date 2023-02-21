import datetime

from django.urls import reverse
from django.utils import timezone

from itou.institutions.factories import InstitutionMembershipFactory
from itou.siae_evaluations import enums as evaluation_enums
from itou.siae_evaluations.factories import EvaluatedSiaeFactory
from itou.siae_evaluations.models import Sanctions
from itou.siaes.factories import SiaeMembershipFactory
from itou.utils.test import TestCase
from itou.utils.types import InclusiveDateRange


class EvaluatedSiaeSanctionViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        institution_membership = InstitutionMembershipFactory(institution__name="DDETS 87")
        cls.institution_user = institution_membership.user
        siae_membership = SiaeMembershipFactory(siae__name="Les petits jardins")
        cls.siae_user = siae_membership.user
        cls.evaluated_siae = EvaluatedSiaeFactory(
            complete=True,
            job_app__criteria__review_state=evaluation_enums.EvaluatedJobApplicationsState.REFUSED_2,
            evaluation_campaign__institution=institution_membership.institution,
            evaluation_campaign__name="Contrôle 2022",
            siae=siae_membership.siae,
            notified_at=timezone.now(),
            notification_reason=evaluation_enums.EvaluatedSiaeNotificationReason.INVALID_PROOF,
            notification_text="A envoyé une photo de son chat. Séparé de son chat pendant une journée.",
        )
        cls.sanctions = Sanctions.objects.create(
            evaluated_siae=cls.evaluated_siae,
            training_session="RDV le 18 avril à 14h dans les locaux de Pôle Emploi.",
        )
        cls.return_evaluated_siae_list_link_html = (
            '<a class="btn btn-primary float-right" '
            f'href="/siae_evaluation/institution_evaluated_siae_list/{cls.evaluated_siae.evaluation_campaign_id}/">'
            "Revenir à la liste des SIAE</a>"
        )
        cls.return_dashboard_link_html = (
            '<a class="btn btn-primary float-right" href="/dashboard/">Retour au Tableau de bord</a>'
        )

    def assertSanctionContent(self, response):
        self.assertContains(
            response,
            '<h1 class="mb-4">Notification de sanction pour <span class="text-info">Les petits jardins</span></h1>',
            html=True,
            count=1,
        )
        self.assertContains(
            response,
            '<b>Résultat :</b> <b class="text-danger">Négatif</b>',
            count=1,
        )
        self.assertContains(
            response,
            '<b>Raison principale :</b> <b class="text-info">Pièce justificative incorrecte</b>',
            count=1,
        )
        self.assertContains(
            response,
            """
            <b>Commentaire de votre DDETS</b>
            <div class="card">
                <div class="card-body">A envoyé une photo de son chat. Séparé de son chat pendant une journée.</div>
            </div>
            """,
            html=True,
            count=1,
        )

    def test_anonymous_view_siae(self):
        url = reverse(
            "siae_evaluations_views:siae_sanction",
            kwargs={"evaluated_siae_pk": self.evaluated_siae.pk},
        )
        response = self.client.get(url)
        self.assertRedirects(response, reverse("account_login") + f"?next={url}")

    def test_anonymous_view_institution(self):
        url = reverse(
            "siae_evaluations_views:institution_evaluated_siae_sanction",
            kwargs={"evaluated_siae_pk": self.evaluated_siae.pk},
        )
        response = self.client.get(url)
        self.assertRedirects(response, reverse("account_login") + f"?next={url}")

    def test_view_as_institution(self):
        self.client.force_login(self.institution_user)
        response = self.client.get(
            reverse(
                "siae_evaluations_views:institution_evaluated_siae_sanction",
                kwargs={"evaluated_siae_pk": self.evaluated_siae.pk},
            )
        )
        self.assertSanctionContent(response)
        self.assertContains(
            response,
            self.return_evaluated_siae_list_link_html,
            html=True,
            count=1,
        )
        self.assertNotContains(
            response,
            self.return_dashboard_link_html,
            html=True,
        )

    def test_view_as_other_institution(self):
        other = InstitutionMembershipFactory()
        self.client.force_login(other.user)
        response = self.client.get(
            reverse(
                "siae_evaluations_views:institution_evaluated_siae_sanction",
                kwargs={"evaluated_siae_pk": self.evaluated_siae.pk},
            )
        )
        assert response.status_code == 404

    def test_view_as_siae(self):
        self.client.force_login(self.siae_user)
        response = self.client.get(
            reverse(
                "siae_evaluations_views:siae_sanction",
                kwargs={"evaluated_siae_pk": self.evaluated_siae.pk},
            )
        )
        self.assertSanctionContent(response)
        self.assertContains(
            response,
            self.return_dashboard_link_html,
            html=True,
            count=1,
        )
        self.assertNotContains(
            response,
            self.return_evaluated_siae_list_link_html,
            html=True,
        )

    def test_view_as_other_siae(self):
        siae_membership = SiaeMembershipFactory()
        self.client.force_login(siae_membership.user)
        response = self.client.get(
            reverse(
                "siae_evaluations_views:siae_sanction",
                kwargs={"evaluated_siae_pk": self.evaluated_siae.pk},
            )
        )
        assert response.status_code == 404

    def test_training_session(self):
        self.client.force_login(self.institution_user)
        response = self.client.get(
            reverse(
                "siae_evaluations_views:institution_evaluated_siae_sanction",
                kwargs={"evaluated_siae_pk": self.evaluated_siae.pk},
            )
        )
        self.assertSanctionContent(response)
        self.assertContains(
            response,
            """
            <div class="card-body">
             <h2>
              Sanction
             </h2>
             <h3 class="mt-5">
              Participation à une session de présentation de l’auto-prescription
             </h3>
             <div class="card">
              <div class="card-body">
               RDV le 18 avril à 14h dans les locaux de Pôle Emploi.
              </div>
             </div>
            </div>
            """,
            html=True,
            count=1,
        )

    def test_temporary_suspension(self):
        self.sanctions.training_session = ""
        self.sanctions.suspension_dates = InclusiveDateRange(datetime.date(2023, 1, 1), datetime.date(2023, 6, 1))
        self.sanctions.save()
        self.client.force_login(self.institution_user)
        response = self.client.get(
            reverse(
                "siae_evaluations_views:institution_evaluated_siae_sanction",
                kwargs={"evaluated_siae_pk": self.evaluated_siae.pk},
            )
        )
        self.assertSanctionContent(response)
        self.assertContains(
            response,
            """
            <div class="card-body">
             <h2>
              Sanction
             </h2>
             <h3 class="mt-5">
              Retrait temporaire de la capacité d’auto-prescription
             </h3>
             <p>
              La capacité d’auto-prescrire un parcours d'insertion par l'activité économique est suspendue pour une
              durée déterminée par l'autorité administrative.
             </p>
             <p>
              Dans votre cas, le retrait temporaire de la capacité d’auto-prescription sera effectif à partir du
              1 janvier 2023 et jusqu’au 1 juin 2023.
             </p>
            </div>
            """,
            html=True,
            count=1,
        )

    def test_permanent_suspension(self):
        self.sanctions.training_session = ""
        self.sanctions.suspension_dates = InclusiveDateRange(datetime.date(2023, 1, 1))
        self.sanctions.save()
        self.client.force_login(self.institution_user)
        response = self.client.get(
            reverse(
                "siae_evaluations_views:institution_evaluated_siae_sanction",
                kwargs={"evaluated_siae_pk": self.evaluated_siae.pk},
            )
        )
        self.assertSanctionContent(response)
        self.assertContains(
            response,
            """
            <div class="card-body">
             <h2>
              Sanction
             </h2>
             <h3 class="mt-5">
              Retrait définitif de la capacité d’auto-prescription
             </h3>
             <p>
              La capacité à prescrire un parcours est rompue, elle peut être rétablie par le préfet, à la demande de la
              structure, sous réserve de la participation de ses dirigeants ou salariés à des actions de formation
              définies par l'autorité administrative.
             </p>
             <p>
              Dans votre cas, le retrait définitif de la capacité d’auto-prescription sera effectif à partir du
              1 janvier 2023.
             </p>
            </div>
            """,
            html=True,
            count=1,
        )

    def test_subsidy_cut_rate(self):
        self.sanctions.training_session = ""
        self.sanctions.subsidy_cut_dates = InclusiveDateRange(datetime.date(2023, 1, 1), datetime.date(2023, 6, 1))
        self.sanctions.subsidy_cut_percent = 35
        self.sanctions.save()
        self.client.force_login(self.institution_user)
        response = self.client.get(
            reverse(
                "siae_evaluations_views:institution_evaluated_siae_sanction",
                kwargs={"evaluated_siae_pk": self.evaluated_siae.pk},
            )
        )
        self.assertSanctionContent(response)
        self.assertContains(
            response,
            """
            <div class="card-body">
             <h2>
              Sanction
             </h2>
             <h3 class="mt-5">
              Suppression d’une partie de l’aide au poste
             </h3>
             <p>
              La suppression de l’aide attribuée aux salariés s’apprécie par l'autorité administrative, par imputation
              de l’année N+1. Cette notification s’accompagne d’une demande conforme auprès de l’ASP de la part du
              préfet. Lorsque le département a participé aux aides financières concernées en application de l'article
              L. 5132-2, le préfet informe le président du conseil départemental de sa décision en vue de la
              récupération, le cas échéant, des montants correspondants.
             </p>
             <p>
              Dans votre cas, la suppression de 35 % de l’aide au poste sera effective à partir du 1 janvier 2023 et
              jusqu’au 1 juin 2023.
             </p>
            </div>
            """,
            html=True,
            count=1,
        )

    def test_subsidy_cut_full(self):
        self.sanctions.training_session = ""
        self.sanctions.subsidy_cut_dates = InclusiveDateRange(datetime.date(2023, 1, 1), datetime.date(2023, 6, 1))
        self.sanctions.subsidy_cut_percent = 100
        self.sanctions.save()
        self.client.force_login(self.institution_user)
        response = self.client.get(
            reverse(
                "siae_evaluations_views:institution_evaluated_siae_sanction",
                kwargs={"evaluated_siae_pk": self.evaluated_siae.pk},
            )
        )
        self.assertSanctionContent(response)
        self.assertContains(
            response,
            """
            <div class="card-body">
             <h2>
              Sanction
             </h2>
             <h3 class="mt-5">
              Suppression de l’aide au poste
             </h3>
             <p>
              La suppression de l’aide attribuée aux salariés s’apprécie par l'autorité administrative, par imputation
              de l’année N+1. Cette notification s’accompagne d’une demande conforme auprès de l’ASP de la part du
              préfet. Lorsque le département a participé aux aides financières concernées en application de l'article
              L. 5132-2, le préfet informe le président du conseil départemental de sa décision en vue de la
              récupération, le cas échéant, des montants correspondants.
             </p>
             <p>
              Dans votre cas, la suppression de l’aide au poste sera effective à partir du 1 janvier 2023 et
              jusqu’au 1 juin 2023.
             </p>
            </div>
            """,
            html=True,
            count=1,
        )

    def test_deactivation(self):
        self.sanctions.training_session = ""
        self.sanctions.deactivation_reason = "Mauvais comportement, rien ne va. On arrête tout."
        self.sanctions.save()
        self.client.force_login(self.institution_user)
        response = self.client.get(
            reverse(
                "siae_evaluations_views:institution_evaluated_siae_sanction",
                kwargs={"evaluated_siae_pk": self.evaluated_siae.pk},
            )
        )
        self.assertSanctionContent(response)
        self.assertContains(
            response,
            """
            <div class="card-body">
             <h2>
              Sanction
             </h2>
             <h3 class="mt-5">
              Déconventionnement de la structure
             </h3>
             <p>
              La suppression du conventionnement s’apprécie par l'autorité administrative. Cette notification
              s’accompagne d’une demande conforme auprès de l’ASP de la part du préfet. Lorsque le département a
              participé aux aides financières concernées en application de l'article L. 5132-2, le préfet informe le
              président du conseil départemental de sa décision.
             </p>
             <div class="card">
              <div class="card-body">
               Mauvais comportement, rien ne va. On arrête tout.
              </div>
             </div>
            </div>
            """,
            html=True,
            count=1,
        )

    def test_no_sanction(self):
        self.sanctions.training_session = ""
        self.sanctions.no_sanction_reason = "Ça ira pour cette fois."
        self.sanctions.save()
        self.client.force_login(self.institution_user)
        response = self.client.get(
            reverse(
                "siae_evaluations_views:institution_evaluated_siae_sanction",
                kwargs={"evaluated_siae_pk": self.evaluated_siae.pk},
            )
        )
        self.assertSanctionContent(response)
        self.assertContains(
            response,
            """
            <div class="card-body">
             <h2>
              Sanctions
             </h2>
             <h3 class="mt-5">
              Ne pas sanctionner
             </h3>
             <div class="card">
              <div class="card-body">
              Ça ira pour cette fois.
              </div>
             </div>
            </div>
            """,
            html=True,
            count=1,
        )


def test_sanctions_helper_view(client):
    response = client.get(reverse("siae_evaluations_views:sanctions_helper"))
    assert response.status_code == 200
