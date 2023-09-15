# Generated by Django 4.2.5 on 2023-09-14 14:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0043_prevent_pe_connect_duplicates"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="address_filled_at",
            field=models.DateTimeField(
                help_text="Mise à jour par autocomplétion de l'utilisateur",
                null=True,
                verbose_name="date de dernier remplissage de l'adresse",
            ),
        ),
    ]
