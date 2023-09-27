# Generated by Django 4.2.5 on 2023-10-03 16:14

import django.contrib.postgres.constraints
import django.contrib.postgres.fields.ranges
from django.db import migrations

import itou.utils.models


class Migration(migrations.Migration):
    dependencies = [
        ("asp", "0005_add_commune_city"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="commune",
            constraint=django.contrib.postgres.constraints.ExclusionConstraint(
                expressions=(
                    (
                        itou.utils.models.DateRange(
                            "start_date",
                            "end_date",
                            django.contrib.postgres.fields.ranges.RangeBoundary(
                                inclusive_lower=True, inclusive_upper=True
                            ),
                        ),
                        "&&",
                    ),
                    ("code", "="),
                ),
                name="exclude_commune_overlapping_dates",
                violation_error_message="La période chevauche une autre période existante pour ce même code INSEE.",
            ),
        ),
        migrations.AddConstraint(
            model_name="department",
            constraint=django.contrib.postgres.constraints.ExclusionConstraint(
                expressions=(
                    (
                        itou.utils.models.DateRange(
                            "start_date",
                            "end_date",
                            django.contrib.postgres.fields.ranges.RangeBoundary(
                                inclusive_lower=True, inclusive_upper=True
                            ),
                        ),
                        "&&",
                    ),
                    ("code", "="),
                ),
                name="exclude_department_overlapping_dates",
                violation_error_message="La période chevauche une autre période existante pour ce même code INSEE.",
            ),
        ),
    ]
