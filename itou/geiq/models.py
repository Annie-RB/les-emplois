from django.db import models

from itou.companies.models import Company
from itou.users.enums import Title


class ContractType(models.TextChoices):

    CPRO = "CPRO", "Contrat de professionnalisation"
    CAPP = "CAPP", "Contrat d'apprentissage"
    CUI_F = "CUI+F", "CUI (toute catégorie)"
    CDD_CPF = "CDD+CPF", "CDD - CPF"
    CDD_AUTRE = "CDD+autre", "CDD - Autre"
    AUTRE_F = "Autre F", "Autre (avec formation)"

    CUI = "CUI", "CUI (toute catégorie)"
    CDD = "CDD", "CDD"
    CDI = "CDI", "CDI"
    AUTRE_SF = "Autre SF", "Autre (sans formation)"


class Qualification(models.TextChoices):

    SQ = "SQ", "Sans qualification"
    N3 = "N3", "Niveau 3 (CAP, BEP)"
    N4 = "N4", "Niveau 4 (BP, Bac Général, Techno ou Pro, BT)"
    N5 = "N5", "Niveau 5 ou + (Bac+2 ou +)"


class PrequalificationAction(models.TextChoices):

    AFPR = "AFPR", "AFPR"
    DISPOSITIF = "DISPOSITIF", "Dispositif régional ou sectoriel"
    POE = "POE", "POE"
    AUTRE = "AUTRE", "Autre"


class PrescriberType(models.TextChoices):

    DEMANDEUR_EMPLOI = "DEMANDEUR_EMPLOI", "Demandeur d'emploi"
    PRESCRIPTEUR = "PRESCRIPTEUR", "Prescripteur"
    EMPLOYEUR = "EMPLOYEUR", "Employeur"
    AUTRE = "AUTRE", "Autre"


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
    company = models.ForeignKey(Company, on_delete=models.PROTECT)  # Match based on SIRET
    last_synced_at = models.DateTimeField(verbose_name="dernière synchronisation à")
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
        verbose_name="niveau de qualification à l'entrée obtenu",
        blank=True,
        default="",
        choices=Qualification.choices,
    )
    prescriber_type = models.CharField(
        verbose_name="type de prescripteur",
        blank=True,
        default="",
        choices=PrescriberType.choices,
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

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = "%s %s" % (self.first_name.strip().title(), self.last_name.upper())
        return full_name.strip()


class EmployeeContract(models.Model):

    label_id = models.IntegerField(verbose_name="id LABEL", primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="contracts")
    antenna = models.ForeignKey(GEIQAntenna, on_delete=models.CASCADE, null=True, related_name="contracts")

    start_at = models.DateTimeField(verbose_name="date de début")
    planned_end_at = models.DateTimeField(verbose_name="date de fin prévisionnelle")
    end_at = models.DateTimeField(verbose_name="date de fin", null=True)
    nb_hours_per_week = models.FloatField(
        verbose_name="nombre d'heures par semaine",
        blank=True,
        null=True,
    )
    contract_type = models.CharField(
        verbose_name="nature du contrat",
        blank=True,
        default="",
        choices=ContractType.choices,
    )

    other_data = models.JSONField(verbose_name="autres données")


class EmployeePrequalification(models.Model):

    label_id = models.IntegerField(verbose_name="id LABEL", primary_key=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="prequalifications")

    action = models.CharField(
        verbose_name="type d'action",
        blank=True,
        default="",
        choices=PrequalificationAction.choices,
    )
    start_at = models.DateTimeField(verbose_name="date de début")
    end_at = models.DateTimeField(verbose_name="date de fin")
    training_hours_nb = models.PositiveIntegerField("nombre d'heures de formation")

    other_data = models.JSONField(verbose_name="autres données")
