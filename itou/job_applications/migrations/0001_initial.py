# Generated by Django 5.0.3 on 2024-03-23 08:28

import uuid

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import django_xworkflows.models
from django.conf import settings
from django.db import migrations, models

import itou.utils.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("approvals", "0001_initial"),
        ("companies", "0001_initial"),
        ("eligibility", "0001_initial"),
        ("prescribers", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="JobApplication",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "state",
                    django_xworkflows.models.StateField(
                        db_index=True,
                        max_length=16,
                        verbose_name="état",
                        workflow=django_xworkflows.models._SerializedWorkflow(
                            initial_state="new",
                            name="JobApplicationWorkflow",
                            states=[
                                "new",
                                "processing",
                                "postponed",
                                "prior_to_hire",
                                "accepted",
                                "refused",
                                "cancelled",
                                "obsolete",
                            ],
                        ),
                    ),
                ),
                ("message", models.TextField(blank=True, verbose_name="message de candidature")),
                ("answer", models.TextField(blank=True, verbose_name="message de réponse")),
                (
                    "created_at",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now, verbose_name="date de création"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, db_index=True, verbose_name="date de modification"),
                ),
                (
                    "job_seeker",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="job_applications",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="demandeur d'emploi",
                    ),
                ),
                (
                    "sender",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="job_applications_sent",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="utilisateur émetteur",
                    ),
                ),
                (
                    "sender_kind",
                    models.CharField(
                        choices=[
                            ("job_seeker", "Demandeur d'emploi"),
                            ("prescriber", "Prescripteur"),
                            ("employer", "Employeur (SIAE)"),
                        ],
                        default="prescriber",
                        max_length=10,
                        verbose_name="type de l'émetteur",
                    ),
                ),
                (
                    "sender_prescriber_organization",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="prescribers.prescriberorganization",
                        verbose_name="organisation du prescripteur émettrice",
                    ),
                ),
                (
                    "refusal_reason",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("did_not_come", "Candidat non joignable"),
                            ("did_not_come_to_interview", "Candidat ne s’étant pas présenté à l’entretien"),
                            ("hired_elsewhere", "Candidat indisponible : en emploi"),
                            ("training", "Candidat indisponible : en formation"),
                            ("non_eligible", "Candidat non éligible"),
                            ("not_mobile", "Candidat non mobile"),
                            ("not_interested", "Candidat non intéressé"),
                            ("lacking_skills", "Le candidat n’a pas les compétences requises pour le poste"),
                            (
                                "incompatible",
                                "Un des freins à l'emploi du candidat est incompatible avec le poste proposé",
                            ),
                            (
                                "prevent_objectives",
                                "L'embauche du candidat empêche la réalisation des objectifs du dialogue de gestion",
                            ),
                            ("no_position", "Pas de recrutement en cours"),
                            ("duplicate", "Candidature en doublon"),
                            ("other", "Autre"),
                            ("approval_expiration_too_close", "La date de fin du PASS IAE / agrément est trop proche"),
                            ("unavailable", "Candidat indisponible ou non intéressé par le poste"),
                            (
                                "eligibility_doubt",
                                "Doute sur l'éligibilité du candidat (penser à renvoyer la personne vers un "
                                "prescripteur)",
                            ),
                            ("deactivation", "La structure n'est plus conventionnée"),
                            ("poorly_informed", "Candidature pas assez renseignée"),
                        ],
                        max_length=30,
                        verbose_name="motifs de refus",
                    ),
                ),
                (
                    "hiring_start_at",
                    models.DateField(blank=True, db_index=True, null=True, verbose_name="date de début du contrat"),
                ),
                (
                    "hiring_end_at",
                    models.DateField(blank=True, null=True, verbose_name="date prévisionnelle de fin du contrat"),
                ),
                (
                    "approval",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="approvals.approval",
                        verbose_name="PASS IAE",
                    ),
                ),
                (
                    "approval_number_sent_by_email",
                    models.BooleanField(default=False, verbose_name="PASS IAE envoyé par email"),
                ),
                (
                    "approval_delivery_mode",
                    models.CharField(
                        blank=True,
                        choices=[("automatic", "Automatique"), ("manual", "Manuel")],
                        max_length=30,
                        verbose_name="mode d'attribution du PASS IAE",
                    ),
                ),
                (
                    "approval_number_sent_at",
                    models.DateTimeField(
                        blank=True, db_index=True, null=True, verbose_name="date d'envoi du PASS IAE"
                    ),
                ),
                (
                    "approval_manually_delivered_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="approval_manually_delivered",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="PASS IAE délivré manuellement par",
                    ),
                ),
                (
                    "hiring_without_approval",
                    models.BooleanField(
                        default=False, verbose_name="l'entreprise choisit de ne pas obtenir un PASS IAE à l'embauche"
                    ),
                ),
                (
                    "approval_manually_refused_at",
                    models.DateTimeField(blank=True, null=True, verbose_name="date de refus manuel du PASS IAE"),
                ),
                (
                    "approval_manually_refused_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="approval_manually_refused",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="PASS IAE refusé manuellement par",
                    ),
                ),
                ("hidden_for_company", models.BooleanField(default=False, verbose_name="masqué coté employeur")),
                ("resume_link", models.URLField(blank=True, max_length=500, verbose_name="lien vers un CV")),
                (
                    "eligibility_diagnosis",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="eligibility.eligibilitydiagnosis",
                        verbose_name="diagnostic d'éligibilité",
                    ),
                ),
                (
                    "answer_to_prescriber",
                    models.TextField(blank=True, verbose_name="message de réponse au prescripteur"),
                ),
                (
                    "create_employee_record",
                    models.BooleanField(default=True, verbose_name="création d'une fiche salarié"),
                ),
                ("transferred_at", models.DateTimeField(blank=True, null=True, verbose_name="date de transfert")),
                (
                    "transferred_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="transférée par",
                    ),
                ),
                (
                    "origin",
                    models.CharField(
                        choices=[
                            ("default", "Créée normalement via les emplois"),
                            ("pe_approval", "Créée lors d'un import d'Agrément Pole Emploi"),
                            ("ai_stock", "Créée lors de l'import du stock AI"),
                            ("admin", "Créée depuis l'admin"),
                        ],
                        default="default",
                        max_length=30,
                        verbose_name="origine de la candidature",
                    ),
                ),
                (
                    "contract_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("APPRENTICESHIP", "Contrat d'apprentissage"),
                            ("PROFESSIONAL_TRAINING", "Contrat de professionalisation"),
                            ("OTHER", "Autre type de contrat"),
                        ],
                        max_length=30,
                        verbose_name="type de contrat",
                    ),
                ),
                (
                    "contract_type_details",
                    models.TextField(blank=True, verbose_name="précisions sur le type de contrat"),
                ),
                (
                    "nb_hours_per_week",
                    models.PositiveSmallIntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(1),
                            django.core.validators.MaxValueValidator(48),
                        ],
                        verbose_name="nombre d'heures par semaine",
                    ),
                ),
                (
                    "geiq_eligibility_diagnosis",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="job_applications",
                        to="eligibility.geiqeligibilitydiagnosis",
                        verbose_name="diagnostic d'éligibilité GEIQ",
                    ),
                ),
                (
                    "prehiring_guidance_days",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="nombre de jours d’accompagnement avant contrat"
                    ),
                ),
                (
                    "planned_training_hours",
                    models.PositiveSmallIntegerField(
                        blank=True, null=True, verbose_name="nombre d'heures de formation prévues"
                    ),
                ),
                (
                    "qualification_level",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("LEVEL_3", "Niveau 3 (CAP, BEP)"),
                            ("LEVEL_4", "Niveau 4 (BP, Bac général, Techno ou Pro, BT)"),
                            ("LEVEL_5", "Niveau 5 ou + (Bac+2 ou +)"),
                            ("NOT_RELEVANT", "Non concerné"),
                        ],
                        max_length=40,
                        verbose_name="niveau de qualification visé",
                    ),
                ),
                (
                    "qualification_type",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("STATE_DIPLOMA", "Diplôme d'état ou titre homologué"),
                            ("CQP", "CQP"),
                            ("CCN", "Positionnement de CCN"),
                        ],
                        max_length=20,
                        verbose_name="type de qualification visé",
                    ),
                ),
                (
                    "inverted_vae_contract",
                    models.BooleanField(blank=True, null=True, verbose_name="contrat associé à une VAE inversée"),
                ),
                (
                    "diagoriente_invite_sent_at",
                    models.DateTimeField(
                        editable=False, null=True, verbose_name="date d'envoi de l'invitation à utiliser Diagoriente"
                    ),
                ),
                (
                    "sender_company",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="companies.company",
                        verbose_name="entreprise émettrice",
                    ),
                ),
                (
                    "to_company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="job_applications_received",
                        to="companies.company",
                        verbose_name="entreprise destinataire",
                    ),
                ),
                (
                    "selected_jobs",
                    models.ManyToManyField(
                        blank=True, to="companies.jobdescription", verbose_name="métiers recherchés"
                    ),
                ),
                (
                    "transferred_from",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="job_application_transferred",
                        to="companies.company",
                        verbose_name="entreprise d'origine",
                    ),
                ),
                (
                    "hired_job",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="hired_job_applications",
                        to="companies.jobdescription",
                        verbose_name="poste retenu",
                    ),
                ),
            ],
            options={
                "verbose_name": "candidature",
                "ordering": ["-created_at"],
            },
            bases=(django_xworkflows.models.BaseWorkflowEnabled, models.Model),
        ),
        migrations.CreateModel(
            name="JobApplicationTransitionLog",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("transition", models.CharField(db_index=True, max_length=255, verbose_name="transition")),
                ("from_state", models.CharField(db_index=True, max_length=255, verbose_name="from state")),
                ("to_state", models.CharField(db_index=True, max_length=255, verbose_name="to state")),
                (
                    "timestamp",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now, verbose_name="performed at"
                    ),
                ),
                (
                    "job_application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="logs",
                        to="job_applications.jobapplication",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "log des transitions de la candidature",
                "verbose_name_plural": "log des transitions des candidatures",
                "ordering": ["-timestamp"],
            },
        ),
        migrations.CreateModel(
            name="PriorAction",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "action",
                    models.TextField(
                        choices=[
                            (
                                "Mise en situation professionnelle",
                                [
                                    ("PROFESSIONAL_SITUATION_EXPERIENCE_PMSMP", "PMSMP"),
                                    ("PROFESSIONAL_SITUATION_EXPERIENCE_MRS", "MRS"),
                                    ("PROFESSIONAL_SITUATION_EXPERIENCE_STAGE", "STAGE"),
                                    ("PROFESSIONAL_SITUATION_EXPERIENCE_OTHER", "Autre"),
                                ],
                            ),
                            (
                                "Pré-qualification",
                                [
                                    ("PREQUALIFICATION_LOCAL_PLAN", "Dispositif régional ou sectoriel"),
                                    ("PREQUALIFICATION_AFPR", "AFPR"),
                                    ("PREQUALIFICATION_POE", "POE"),
                                    ("PREQUALIFICATION_OTHER", "Autre"),
                                ],
                            ),
                        ],
                        verbose_name="action",
                    ),
                ),
                ("dates", itou.utils.models.InclusiveDateRangeField(verbose_name="dates")),
                (
                    "job_application",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="prior_actions",
                        to="job_applications.jobapplication",
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="jobapplication",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(
                        ("contract_type__in", ["PROFESSIONAL_TRAINING", "APPRENTICESHIP"]),
                        ("contract_type_details", ""),
                        ("nb_hours_per_week__gt", 0),
                    ),
                    models.Q(
                        ("contract_type", "OTHER"),
                        ("nb_hours_per_week__gt", 0),
                        models.Q(("contract_type_details", ""), _negated=True),
                    ),
                    models.Q(("contract_type", ""), ("contract_type_details", ""), ("nb_hours_per_week", None)),
                    _connector="OR",
                ),
                name="geiq_fields_coherence",
                violation_error_message="Incohérence dans les champs concernant le contrat GEIQ",
            ),
        ),
        migrations.AddConstraint(
            model_name="jobapplication",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("eligibility_diagnosis__isnull", False),
                    ("geiq_eligibility_diagnosis__isnull", False),
                    _negated=True,
                ),
                name="diagnoses_coherence",
                violation_error_message="Une candidature ne peut avoir les deux types de diagnostics (IAE et GEIQ)",
            ),
        ),
        migrations.AddConstraint(
            model_name="jobapplication",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("qualification_level", "NOT_RELEVANT"), ("qualification_type", "STATE_DIPLOMA"), _negated=True
                ),
                name="qualification_coherence",
                violation_error_message="Incohérence dans les champs concernant la qualification pour le contrat GEIQ",
            ),
        ),
    ]
