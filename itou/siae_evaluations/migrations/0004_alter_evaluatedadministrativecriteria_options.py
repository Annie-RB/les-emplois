# Generated by Django 4.0.3 on 2022-05-03 16:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("siae_evaluations", "0003_alter_evaluatedeligibilitydiagnosis_unique_together"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="evaluatedadministrativecriteria",
            options={
                "ordering": ["evaluated_job_application", "administrative_criteria"],
                "verbose_name": "Critère administratif",
                "verbose_name_plural": "Critères administratifs",
            },
        ),
    ]
