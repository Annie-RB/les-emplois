# Generated by Django 4.1.8 on 2023-06-08 14:32

from django.db import migrations


def update_institution_kind(apps, _schema_editor):
    from itou.institutions import enums

    Institution = apps.get_model("institutions", "Institution")
    Institution.objects.filter(kind="DDETS").update(kind=enums.InstitutionKind.DDETS_IAE)
    Institution.objects.filter(kind="DREETS").update(kind=enums.InstitutionKind.DREETS_IAE)


class Migration(migrations.Migration):

    dependencies = [
        ("institutions", "0005_alter_institution_kind"),
    ]

    operations = [
        migrations.RunPython(update_institution_kind, migrations.RunPython.noop, elidable=True),
    ]
