# Generated by Django 4.1.4 on 2022-12-16 12:59

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models

import itou.employee_record.models
import itou.utils.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("job_applications", "0001_initial"),
        ("siaes", "0044_auto_20210202_1142"),
    ]

    operations = [
        migrations.CreateModel(
            name="EmployeeRecord",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.now, verbose_name="Date de création"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(default=django.utils.timezone.now, verbose_name="Date de modification"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("NEW", "Nouvelle"),
                            ("READY", "Complétée"),
                            ("SENT", "Envoyée"),
                            ("REJECTED", "En erreur"),
                            ("PROCESSED", "Intégrée"),
                            ("DISABLED", "Désactivée"),
                            ("ARCHIVED", "Archivée"),
                        ],
                        default="NEW",
                        max_length=10,
                        verbose_name="Statut",
                    ),
                ),
                ("approval_number", models.CharField(max_length=12, verbose_name="Numéro d'agrément")),
                ("asp_id", models.PositiveIntegerField(verbose_name="Identifiant ASP de la SIAE")),
                (
                    "asp_processing_code",
                    models.CharField(max_length=4, null=True, verbose_name="Code de traitement ASP"),
                ),
                ("archived_json", models.JSONField(null=True, verbose_name="Archive JSON de la fiche salarié")),
                (
                    "job_application",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="employee_record",
                        to="job_applications.jobapplication",
                        verbose_name="Candidature / embauche",
                    ),
                ),
                (
                    "financial_annex",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="siaes.siaefinancialannex",
                        verbose_name="Annexe financière",
                    ),
                ),
                (
                    "asp_batch_line_number",
                    models.IntegerField(
                        db_index=True, null=True, verbose_name="Ligne correspondante dans le fichier batch ASP"
                    ),
                ),
                (
                    "asp_batch_file",
                    models.CharField(
                        db_index=True,
                        max_length=27,
                        null=True,
                        validators=[itou.employee_record.models.validate_asp_batch_filename],
                        verbose_name="Fichier de batch ASP",
                    ),
                ),
                ("processed_at", models.DateTimeField(null=True, verbose_name="Date d'intégration")),
                (
                    "siret",
                    models.CharField(
                        db_index=True,
                        max_length=14,
                        validators=[itou.utils.validators.validate_siret],
                        verbose_name="Siret structure mère",
                    ),
                ),
                (
                    "asp_processing_label",
                    models.CharField(max_length=200, null=True, verbose_name="Libellé de traitement ASP"),
                ),
                ("processed_as_duplicate", models.BooleanField(default=False, verbose_name="Déjà intégrée par l'ASP")),
            ],
            options={
                "ordering": ["-created_at"],
                "verbose_name": "Fiche salarié",
                "verbose_name_plural": "Fiches salarié",
                "unique_together": {("asp_batch_file", "asp_batch_line_number")},
            },
        ),
        migrations.CreateModel(
            name="EmployeeRecordUpdateNotification",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.now, verbose_name="Date de création"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(default=django.utils.timezone.now, verbose_name="Date de modification"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("NEW", "Nouvelle"),
                            ("SENT", "Envoyée"),
                            ("PROCESSED", "Intégrée"),
                            ("REJECTED", "En erreur"),
                        ],
                        default="NEW",
                        max_length=10,
                        verbose_name="Statut",
                    ),
                ),
                (
                    "notification_type",
                    models.CharField(
                        choices=[
                            ("APPROVAL", "Modification du PASS IAE"),
                            ("JOB_SEEKER", "Modification de l'employé"),
                        ],
                        max_length=20,
                        verbose_name="Type de notification",
                    ),
                ),
                (
                    "asp_processing_code",
                    models.CharField(max_length=4, null=True, verbose_name="Code de traitement ASP"),
                ),
                (
                    "asp_processing_label",
                    models.CharField(max_length=200, null=True, verbose_name="Libellé de traitement ASP"),
                ),
                (
                    "asp_batch_file",
                    models.CharField(
                        max_length=27,
                        null=True,
                        validators=[itou.employee_record.models.validate_asp_batch_filename],
                        verbose_name="Fichier de batch ASP",
                    ),
                ),
                (
                    "asp_batch_line_number",
                    models.IntegerField(null=True, verbose_name="Ligne correspondante dans le fichier batch ASP"),
                ),
                (
                    "employee_record",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="update_notifications",
                        to="employee_record.employeerecord",
                        verbose_name="Fiche salarié",
                    ),
                ),
            ],
            options={
                "verbose_name": "Notification de changement de la fiche salarié",
                "verbose_name_plural": "Notifications de changement de la fiche salarié",
            },
        ),
        migrations.AddConstraint(
            model_name="employeerecord",
            constraint=models.UniqueConstraint(
                condition=models.Q(("status", "DISABLED"), _negated=True),
                fields=("asp_id", "approval_number"),
                name="unique_asp_id_approval_number",
            ),
        ),
    ]
