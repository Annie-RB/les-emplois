# Generated by Django 5.0.3 on 2024-03-21 09:50

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("approvals", "0002_fill_approval_updated_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="approval",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="date de modification"),
        ),
    ]
