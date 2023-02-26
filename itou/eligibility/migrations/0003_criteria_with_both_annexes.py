# Generated by Django 4.1.5 on 2023-01-25 15:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("eligibility", "0002_geiq_eligibility_models"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="geiqadministrativecriteria",
            name="ac_level_annex_coherence",
        ),
        migrations.AlterField(
            model_name="geiqadministrativecriteria",
            name="annex",
            field=models.CharField(
                choices=[
                    ("0", "Aucune annexe associée"),
                    ("1", "Annexe 1"),
                    ("2", "Annexe 2"),
                    ("3", "Annexes 1 et 2"),
                ],
                default="1",
                max_length=1,
                verbose_name="Annexe",
            ),
        ),
        migrations.AddConstraint(
            model_name="geiqadministrativecriteria",
            constraint=models.CheckConstraint(
                check=models.Q(
                    models.Q(("annex", "1"), ("level__isnull", True)),
                    models.Q(("annex", "2"), ("level__isnull", False)),
                    models.Q(("annex", "0"), ("level__isnull", True)),
                    ("annex", "3"),
                    _connector="OR",
                ),
                name="ac_level_annex_coherence",
                violation_error_message="Incohérence entre l'annexe du critère administratif et son niveau",
            ),
        ),
    ]
