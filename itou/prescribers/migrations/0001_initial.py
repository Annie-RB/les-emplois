# Generated by Django 5.0.3 on 2024-03-22 09:48

import uuid

import django.contrib.gis.db.models.fields
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import itou.utils.validators


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("cities", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="PrescriberMembership",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("joined_at", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date d'adhésion")),
                ("is_admin", models.BooleanField(default=False, verbose_name="administrateur")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ("is_active", models.BooleanField(default=True, verbose_name="rattachement actif")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="date de modification")),
                (
                    "updated_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="updated_prescribermembership_set",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="mis à jour par",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.now, verbose_name="date de création"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="PrescriberOrganization",
            fields=[
                ("address_line_1", models.CharField(blank=True, max_length=255, verbose_name="adresse")),
                (
                    "address_line_2",
                    models.CharField(
                        blank=True,
                        help_text="Appartement, suite, bloc, bâtiment, boite postale, etc.",
                        max_length=255,
                        verbose_name="complément d'adresse",
                    ),
                ),
                (
                    "post_code",
                    models.CharField(
                        blank=True,
                        max_length=5,
                        validators=[itou.utils.validators.validate_post_code],
                        verbose_name="code postal",
                    ),
                ),
                ("city", models.CharField(blank=True, max_length=255, verbose_name="ville")),
                (
                    "department",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("01", "01 - Ain"),
                            ("02", "02 - Aisne"),
                            ("03", "03 - Allier"),
                            ("04", "04 - Alpes-de-Haute-Provence"),
                            ("05", "05 - Hautes-Alpes"),
                            ("06", "06 - Alpes-Maritimes"),
                            ("07", "07 - Ardèche"),
                            ("08", "08 - Ardennes"),
                            ("09", "09 - Ariège"),
                            ("10", "10 - Aube"),
                            ("11", "11 - Aude"),
                            ("12", "12 - Aveyron"),
                            ("13", "13 - Bouches-du-Rhône"),
                            ("14", "14 - Calvados"),
                            ("15", "15 - Cantal"),
                            ("16", "16 - Charente"),
                            ("17", "17 - Charente-Maritime"),
                            ("18", "18 - Cher"),
                            ("19", "19 - Corrèze"),
                            ("2A", "2A - Corse-du-Sud"),
                            ("2B", "2B - Haute-Corse"),
                            ("21", "21 - Côte-d'Or"),
                            ("22", "22 - Côtes-d'Armor"),
                            ("23", "23 - Creuse"),
                            ("24", "24 - Dordogne"),
                            ("25", "25 - Doubs"),
                            ("26", "26 - Drôme"),
                            ("27", "27 - Eure"),
                            ("28", "28 - Eure-et-Loir"),
                            ("29", "29 - Finistère"),
                            ("30", "30 - Gard"),
                            ("31", "31 - Haute-Garonne"),
                            ("32", "32 - Gers"),
                            ("33", "33 - Gironde"),
                            ("34", "34 - Hérault"),
                            ("35", "35 - Ille-et-Vilaine"),
                            ("36", "36 - Indre"),
                            ("37", "37 - Indre-et-Loire"),
                            ("38", "38 - Isère"),
                            ("39", "39 - Jura"),
                            ("40", "40 - Landes"),
                            ("41", "41 - Loir-et-Cher"),
                            ("42", "42 - Loire"),
                            ("43", "43 - Haute-Loire"),
                            ("44", "44 - Loire-Atlantique"),
                            ("45", "45 - Loiret"),
                            ("46", "46 - Lot"),
                            ("47", "47 - Lot-et-Garonne"),
                            ("48", "48 - Lozère"),
                            ("49", "49 - Maine-et-Loire"),
                            ("50", "50 - Manche"),
                            ("51", "51 - Marne"),
                            ("52", "52 - Haute-Marne"),
                            ("53", "53 - Mayenne"),
                            ("54", "54 - Meurthe-et-Moselle"),
                            ("55", "55 - Meuse"),
                            ("56", "56 - Morbihan"),
                            ("57", "57 - Moselle"),
                            ("58", "58 - Nièvre"),
                            ("59", "59 - Nord"),
                            ("60", "60 - Oise"),
                            ("61", "61 - Orne"),
                            ("62", "62 - Pas-de-Calais"),
                            ("63", "63 - Puy-de-Dôme"),
                            ("64", "64 - Pyrénées-Atlantiques"),
                            ("65", "65 - Hautes-Pyrénées"),
                            ("66", "66 - Pyrénées-Orientales"),
                            ("67", "67 - Bas-Rhin"),
                            ("68", "68 - Haut-Rhin"),
                            ("69", "69 - Rhône"),
                            ("70", "70 - Haute-Saône"),
                            ("71", "71 - Saône-et-Loire"),
                            ("72", "72 - Sarthe"),
                            ("73", "73 - Savoie"),
                            ("74", "74 - Haute-Savoie"),
                            ("75", "75 - Paris"),
                            ("76", "76 - Seine-Maritime"),
                            ("77", "77 - Seine-et-Marne"),
                            ("78", "78 - Yvelines"),
                            ("79", "79 - Deux-Sèvres"),
                            ("80", "80 - Somme"),
                            ("81", "81 - Tarn"),
                            ("82", "82 - Tarn-et-Garonne"),
                            ("83", "83 - Var"),
                            ("84", "84 - Vaucluse"),
                            ("85", "85 - Vendée"),
                            ("86", "86 - Vienne"),
                            ("87", "87 - Haute-Vienne"),
                            ("88", "88 - Vosges"),
                            ("89", "89 - Yonne"),
                            ("90", "90 - Territoire de Belfort"),
                            ("91", "91 - Essonne"),
                            ("92", "92 - Hauts-de-Seine"),
                            ("93", "93 - Seine-Saint-Denis"),
                            ("94", "94 - Val-de-Marne"),
                            ("95", "95 - Val-d'Oise"),
                            ("971", "971 - Guadeloupe"),
                            ("972", "972 - Martinique"),
                            ("973", "973 - Guyane"),
                            ("974", "974 - La Réunion"),
                            ("975", "975 - Saint-Pierre-et-Miquelon"),
                            ("976", "976 - Mayotte"),
                            ("977", "977 - Saint-Barthélémy"),
                            ("978", "978 - Saint-Martin"),
                            ("984", "984 - Terres australes et antarctiques françaises"),
                            ("986", "986 - Wallis-et-Futuna"),
                            ("987", "987 - Polynésie française"),
                            ("988", "988 - Nouvelle-Calédonie"),
                            ("989", "989 - Île Clipperton"),
                        ],
                        db_index=True,
                        max_length=3,
                        verbose_name="département",
                    ),
                ),
                (
                    "coords",
                    django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, null=True, srid=4326),
                ),
                ("geocoding_score", models.FloatField(blank=True, null=True, verbose_name="score du geocoding")),
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "siret",
                    models.CharField(
                        blank=True,
                        max_length=14,
                        null=True,
                        validators=[itou.utils.validators.validate_siret],
                        verbose_name="siret",
                    ),
                ),
                ("name", models.CharField(max_length=255, verbose_name="nom")),
                ("phone", models.CharField(blank=True, max_length=20, verbose_name="téléphone")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="e-mail")),
                ("website", models.URLField(blank=True, verbose_name="site web")),
                ("description", models.TextField(blank=True, verbose_name="description")),
                (
                    "is_authorized",
                    models.BooleanField(
                        default=False,
                        help_text="Précise si l'organisation est habilitée.",
                        verbose_name="habilitation",
                    ),
                ),
                (
                    "members",
                    models.ManyToManyField(
                        blank=True,
                        through="prescribers.PrescriberMembership",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="membres",
                    ),
                ),
                (
                    "code_safir_pole_emploi",
                    models.CharField(
                        blank=True,
                        help_text="Code unique d'une agence France Travail.",
                        max_length=5,
                        null=True,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                "^[0-9]{5}$", "Le code SAFIR doit être composé de 5 chiffres."
                            )
                        ],
                        verbose_name="code Safir",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.now, verbose_name="date de création"),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_prescriber_organization_set",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="créé par",
                    ),
                ),
                (
                    "kind",
                    models.CharField(
                        choices=[
                            ("AFPA", "AFPA - Agence nationale pour la formation professionnelle des adultes"),
                            ("ASE", "ASE - Aide sociale à l'enfance"),
                            ("Orienteur", "Autre organisation (orienteur)"),
                            (
                                "CAARUD",
                                "CAARUD - Centre d'accueil et d'accompagnement à la réduction de risques pour usagers "
                                "de drogues",
                            ),
                            ("CADA", "CADA - Centre d'accueil de demandeurs d'asile"),
                            ("CAF", "CAF - Caisse d'allocations familiales"),
                            ("CAP_EMPLOI", "Cap emploi"),
                            ("CAVA", "CAVA - Centre d'adaptation à la vie active"),
                            (
                                "CCAS",
                                "CCAS - Centre communal d'action sociale ou centre intercommunal d'action sociale",
                            ),
                            ("CHRS", "CHRS - Centre d'hébergement et de réinsertion sociale"),
                            ("CHU", "CHU - Centre d'hébergement d'urgence"),
                            ("CIDFF", "CIDFF - Centre d'information sur les droits des femmes et des familles"),
                            ("CPH", "CPH - Centre provisoire d'hébergement"),
                            ("CSAPA", "CSAPA - Centre de soins, d'accompagnement et de prévention en addictologie"),
                            ("E2C", "E2C - École de la deuxième chance"),
                            ("EPIDE", "EPIDE - Établissement pour l'insertion dans l'emploi"),
                            ("PE", "France Travail"),
                            ("HUDA", "HUDA - Hébergement d'urgence pour demandeurs d'asile"),
                            ("ML", "Mission locale"),
                            ("MSA", "MSA - Mutualité Sociale Agricole"),
                            (
                                "OACAS",
                                "OACAS - Structure porteuse d'un agrément national organisme d'accueil communautaire "
                                "et d'activité solidaire",
                            ),
                            ("OIL", "Opérateur d'intermédiation locative"),
                            (
                                "ODC",
                                "Organisation délégataire d'un Conseil Départemental (Orientation et suivi des BRSA)",
                            ),
                            ("OHPD", "Organisme habilité par le préfet de département"),
                            (
                                "OCASF",
                                "Organisme mentionné au 8° du I de l’article L. 312-1 du code de l’action sociale et "
                                "des familles",
                            ),
                            ("PENSION", "Pension de famille / résidence accueil"),
                            ("PIJ_BIJ", "PIJ-BIJ - Point/Bureau information jeunesse"),
                            ("PJJ", "PJJ - Protection judiciaire de la jeunesse"),
                            ("PLIE", "PLIE - Plan local pour l'insertion et l'emploi"),
                            ("RS_FJT", "Résidence sociale / FJT - Foyer de Jeunes Travailleurs"),
                            ("PREVENTION", "Service ou club de prévention"),
                            ("DEPT", "Service social du conseil départemental"),
                            ("SPIP", "SPIP - Service pénitentiaire d'insertion et de probation"),
                            ("Autre", "Autre"),
                        ],
                        default="Autre",
                        max_length=20,
                        verbose_name="type",
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="date de modification")),
                (
                    "authorization_status",
                    models.CharField(
                        choices=[
                            ("NOT_SET", "Habilitation en attente de validation"),
                            ("VALIDATED", "Habilitation validée"),
                            ("REFUSED", "Validation de l'habilitation refusée"),
                            ("NOT_REQUIRED", "Pas d'habilitation nécessaire"),
                        ],
                        default="NOT_SET",
                        max_length=20,
                        verbose_name="statut de l'habilitation",
                    ),
                ),
                (
                    "authorization_updated_at",
                    models.DateTimeField(null=True, verbose_name="date de MAJ du statut de l'habilitation"),
                ),
                (
                    "authorization_updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="authorization_status_set",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="dernière MAJ de l'habilitation par",
                    ),
                ),
                (
                    "is_brsa",
                    models.BooleanField(
                        default=False,
                        help_text="Indique si l'organisme est conventionné par le conseil départemental pour le suivi "
                        "des BRSA.",
                        verbose_name="conventionné pour le suivi des BRSA",
                    ),
                ),
                (
                    "is_head_office",
                    models.BooleanField(
                        default=False,
                        help_text="Information obtenue via API Entreprise.",
                        verbose_name="siège de l'entreprise",
                    ),
                ),
                ("uid", models.UUIDField(db_index=True, default=uuid.uuid4, unique=True)),
                (
                    "ban_api_resolved_address",
                    models.TextField(
                        blank=True, null=True, verbose_name="libellé d'adresse retourné par le dernier geocoding"
                    ),
                ),
                (
                    "geocoding_updated_at",
                    models.DateTimeField(blank=True, null=True, verbose_name="dernière modification du geocoding"),
                ),
                (
                    "insee_city",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="cities.city"
                    ),
                ),
            ],
            options={
                "verbose_name": "organisation",
                "unique_together": {("siret", "kind")},
            },
        ),
        migrations.AddField(
            model_name="prescribermembership",
            name="organization",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="prescribers.prescriberorganization"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="prescribermembership",
            unique_together={("user_id", "organization_id")},
        ),
        migrations.AddConstraint(
            model_name="prescriberorganization",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("authorization_status", "VALIDATED"), ("is_brsa", False), ("kind", "ODC"), _negated=True
                ),
                name="validated_odc_is_brsa",
                violation_error_message="Une organisation habilitée délégataire d'un Conseil Départemental doit être "
                "conventionnée pour le suivi des BRSA.",
            ),
        ),
    ]
