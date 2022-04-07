# Generated by Django 4.0.3 on 2022-04-12 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("approvals", "0028_mergedpoleemploiapproval_and_more"),
    ]

    operations = [
        migrations.RenameModel(
            old_name="MergedPoleEmploiApproval",
            new_name="OriginalPoleEmploiApproval",
        ),
        migrations.AlterModelOptions(
            name="originalpoleemploiapproval",
            options={
                "ordering": ["-start_at"],
                "verbose_name": "Agrément Pôle emploi original",
                "verbose_name_plural": "Agréments Pôle emploi originaux",
            },
        ),
        migrations.RemoveField(
            model_name="poleemploiapproval",
            name="merged",
        ),
        migrations.AlterField(
            model_name="poleemploiapproval",
            name="number",
            field=models.CharField(max_length=12, unique=True, verbose_name="Numéro"),
        ),
    ]
