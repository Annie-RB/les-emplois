# Generated by Django 5.0.3 on 2024-03-22 09:37

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="InclusionConnectState",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "created_at",
                    models.DateTimeField(
                        db_index=True, default=django.utils.timezone.now, verbose_name="date de création"
                    ),
                ),
                ("used_at", models.DateTimeField(null=True, verbose_name="date d'utilisation")),
                ("data", models.JSONField(blank=True, default=dict, verbose_name="données de session")),
                ("state", models.CharField(max_length=12, unique=True)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
