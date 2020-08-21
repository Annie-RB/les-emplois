# Generated by Django 3.1 on 2020-08-21 14:16

import datetime

from django.db import migrations

from itou.siaes.models import Siae


def fix_siae_source(apps, schema_editor):
    for siae in Siae.objects.filter(source=Siae.SOURCE_USER_CREATED):
        user = siae.created_by
        if user:
            assert not user.is_prescriber
            assert not user.is_superuser
            if user.is_siae_staff:
                # Siae created by a regular siae user - do not touch.
                assert not user.is_job_seeker
                assert not user.is_staff
            else:
                # Siae created by our staff. Should be STAFF_CREATED.
                assert user.is_staff
                # Some staff users are job seekers ¯\_(ツ)_/¯
                # assert not user.is_job_seeker
                siae.source = Siae.SOURCE_STAFF_CREATED
                siae.save()
        else:
            # Siae created by a user which no longer exists.
            # This only happened before the "create siae" feature was
            # introduced and should no longer happen ever.
            assert siae.created_at.date() < datetime.date(2019, 12, 31)
            siae.source = Siae.SOURCE_STAFF_CREATED
            siae.save()


class Migration(migrations.Migration):

    dependencies = [
        ("siaes", "0028_auto_20200821_1616"),
    ]

    operations = [migrations.RunPython(fix_siae_source, migrations.RunPython.noop)]
