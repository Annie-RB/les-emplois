# Generated by Django 4.2.9 on 2024-01-19 11:51

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0035_alter_jobseekerprofile_lack_of_nir_reason_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="user",
            name="unique_nir_if_not_empty",
        ),
        migrations.RemoveConstraint(
            model_name="user",
            name="user_lack_of_nir_reason_or_nir",
        ),
        migrations.RemoveField(
            model_name="user",
            name="lack_of_nir_reason",
        ),
        migrations.RemoveField(
            model_name="user",
            name="nir",
        ),
    ]
