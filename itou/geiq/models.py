from django.db import models

from itou.users.enums import Title


class Qualification(models.TextChoices):

    SQ = "SQ", "Sans qualification"
    N3 = "N3", "Niveau 3 (CAP, BEP)"
    N4 = "N4", "Niveau 4 (BP, Bac Général, Techno ou Pro, BT)"
    N5 = "N5", "Niveau 5 ou + (Bac+2 ou +)"


class GEIQAddressMixin(models.Model):
    address_line_1 = models.CharField(verbose_name="adresse", max_length=255, blank=True)
    address_line_2 = models.CharField(
        verbose_name="complément d'adresse",
        max_length=255,
        blank=True,
        help_text="Appartement, suite, bloc, bâtiment, boite postale, etc.",
    )
    post_code = models.CharField(
        verbose_name="code postal",
        max_length=5,
        blank=True,
    )
    city = models.CharField(verbose_name="ville", max_length=255, blank=True)

    class Meta:
        abstract = True


class GEIQLabelInfo(GEIQAddressMixin, models.Model):

    label_id = models.IntegerField(verbose_name="id LABEL", primary_key=True)
    name = models.CharField(verbose_name="nom")
    created_at = models.DateTimeField("date de création", null=True)
    siret = models.CharField(verbose_name="siret", blank=True)
    phone = models.CharField(verbose_name="téléphone", max_length=20, blank=True)
    email = models.EmailField(verbose_name="e-mail", blank=True)

    ffgeiq_member = models.BooleanField("adherent FFGEIQ")
    other_data = models.JSONField(verbose_name="autres données")


class GEIQAntenna(GEIQAddressMixin, models.Model):

    label_id = models.IntegerField(verbose_name="id LABEL", primary_key=True)
    geiq = models.ForeignKey(GEIQLabelInfo, on_delete=models.CASCADE, related_name="antennas")
    name = models.CharField(verbose_name="nom")
    created_at = models.DateTimeField("date de création", null=True)
    siret = models.CharField(verbose_name="siret", blank=True)
    phone = models.CharField(verbose_name="téléphone", max_length=20, blank=True)
    email = models.EmailField(verbose_name="e-mail", blank=True)


class Employee(GEIQAddressMixin, models.Model):

    label_id = models.IntegerField(verbose_name="id LABEL", primary_key=True)
    geiq = models.ForeignKey(GEIQLabelInfo, on_delete=models.CASCADE, related_name="employees")
    created_at = models.DateTimeField("date de création", null=True)
    last_name = models.CharField(verbose_name="nom de famille")
    first_name = models.CharField(verbose_name="prénom")
    birthdate = models.DateField(verbose_name="date de naissance")
    title = models.CharField(
        max_length=3,
        verbose_name="civilité",
        blank=True,
        default="",
        choices=Title.choices,
    )
    qualification = models.CharField(
        max_length=2,
        verbose_name="niveau de qualifacation à l'entrée obtenu",
        blank=True,
        default="",
        choices=Qualification.choices,
    )

    # 'numero': '64',
    # 'prescripteur': {'id': 13, 'libelle': 'Autres', 'libelle_abr': 'AUTRE'},
    # 'prescripteur_autre': '1 Autres',
    # 'is_bac_general': None,
    # 'statuts_prioritaire': [
    #   {'id': 1, 'libelle': 'Personne éloignée du marché du travail (> 1 an)', 'libelle_abr': 'DELD', 'niveau': 99},
    #   {'id': 2, 'libelle': 'Bénéficiaire de minima sociaux', 'libelle_abr': 'MINSOC', 'niveau': 99},
    #  ],
    # 'precision_status_prio': None,
    # 'identifiant': 'BLANC Juste',
    # 'identifiant_sans_accent': 'BLANC Juste',
    # 'is_imported': None},
    other_data = models.JSONField(verbose_name="autres données")


class EmployeeContract(models.Model):

    label_id = models.IntegerField(verbose_name="id LABEL", primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="contracts")
    antenna = models.ForeignKey(GEIQAntenna, on_delete=models.CASCADE, null=True, related_name="contracts")

    other_data = models.JSONField(verbose_name="autres données")
