import datetime

from itou.users.enums import Title
from itou.utils.apis import geiq_label
from itou.utils.sync import DiffItemKind, yield_sync_diff

from . import models


def convert_ms_timestamp_to_datetime(nb_ms):
    if not nb_ms:
        return None
    return datetime.datetime.fromtimestamp(nb_ms / 1000, tz=datetime.timezone.utc)


GEIQ_MAPPING = {
    "label_id": "id",
    "name": "nom",
    "created_at": "date_creation",
    "siret": "siret",
    "address_line_1": "adresse",
    "address_line_2": "adresse2",
    "post_code": "cp",
    "city": "ville",
    "phone": "telephone",
    "email": "email",
    "ffgeiq_member": "is_adherent_ffgeiq",
}


def label_data_to_django(data, *, mapping, model, with_other_data=False):
    model_data = {}
    if with_other_data:
        other_data = dict(data)
    for db_key, label_key in mapping.items():
        model_data[db_key] = data[label_key]
        if with_other_data:
            other_data.pop(label_key)
    if with_other_data:
        model_data["other_data"] = other_data
    return model(**model_data)


ANTENNA_MAPPING = {
    "label_id": "id",
    "geiq_id": "geiq_id",
    "name": "nom",
    "created_at": "date_creation",
    "siret": "siret",
    "address_line_1": "adresse",
    "address_line_2": "adresse2",
    "post_code": "cp",
    "city": "ville",
    "phone": "telephone",
    "email": "email",
}


def normalize_null_values(value):
    if value is None:
        return ""
    return value


def sync_geiqs_and_antennas():
    client = geiq_label.get_client()
    geiq_infos = client.get_all_geiq()

    antenna_infos = []
    for geiq_info in geiq_infos:
        for key in (
            "siret",
            "telephone",
            "email",
            "adresse2",
        ):
            geiq_info[key] = normalize_null_values(geiq_info[key])
        geiq_info["date_creation"] = convert_ms_timestamp_to_datetime(geiq_info["date_creation"])
        antenne_infos = geiq_info.pop("antennes")
        for antenne_info in antenne_infos:
            assert antenne_info["geiq_id"] == geiq_info["id"], antenne_info
            for key in (
                "siret",
                "telephone",
                "email",
                "adresse2",
            ):
                antenne_info[key] = normalize_null_values(antenne_info[key])
            antenne_info["date_creation"] = convert_ms_timestamp_to_datetime(antenne_info["date_creation"])
        antenna_infos.extend(antenne_infos)

    geiqs_to_create = []
    geiqs_to_update = []
    geiqs_to_delete = []

    for item in yield_sync_diff(
        geiq_infos,
        "id",
        models.GEIQLabelInfo.objects.all(),
        "label_id",
        [(col_key, db_key) for db_key, col_key in GEIQ_MAPPING.items()],
    ):
        if item.kind in [DiffItemKind.ADDITION, DiffItemKind.EDITION]:
            geiq = label_data_to_django(
                item.raw, mapping=GEIQ_MAPPING, model=models.GEIQLabelInfo, with_other_data=True
            )
            if item.kind == DiffItemKind.ADDITION:
                geiqs_to_create.append(geiq)
            else:
                geiq.pk = item.db_obj.pk
                geiqs_to_update.append(geiq)
                print(item)
        elif item.kind == DiffItemKind.DELETION:
            geiqs_to_delete.add(item.key)

    print(f"Would create {len(geiqs_to_create)}")
    print(f"Would update {len(geiqs_to_update)}")
    print(f"Would delete {len(geiqs_to_delete)}")
    models.GEIQLabelInfo.objects.bulk_create(geiqs_to_create)
    models.GEIQLabelInfo.objects.bulk_update(
        geiqs_to_update, {db_key for db_key in GEIQ_MAPPING if db_key != "label_id"}
    )

    antennas_to_create = []
    antennas_to_update = []
    antennas_to_delete = []

    for item in yield_sync_diff(
        antenna_infos,
        "id",
        models.GEIQAntenna.objects.all(),
        "label_id",
        [(col_key, db_key) for db_key, col_key in ANTENNA_MAPPING.items()],
    ):
        if item.kind in [DiffItemKind.ADDITION, DiffItemKind.EDITION]:
            antenna = label_data_to_django(item.raw, mapping=ANTENNA_MAPPING, model=models.GEIQAntenna)
            if item.kind == DiffItemKind.ADDITION:
                antennas_to_create.append(antenna)
            else:
                antenna.pk = item.db_obj.pk
                antennas_to_update.append(antenna)
                print(item)
        elif item.kind == DiffItemKind.DELETION:
            antennas_to_delete.add(item.key)

    print(f"Would create {len(antennas_to_create)}")
    print(f"Would update {len(antennas_to_update)}")
    print(f"Would delete {len(antennas_to_delete)}")
    models.GEIQAntenna.objects.bulk_create(antennas_to_create)
    models.GEIQAntenna.objects.bulk_update(
        antennas_to_update, {db_key for db_key in ANTENNA_MAPPING if db_key != "label_id"}
    )


# Employee's other_data example:
# 'numero': '123',
# 'prescripteur': {'id': 13, 'libelle': 'Autres', 'libelle_abr': 'AUTRE'},
# 'prescripteur_autre': '1 Autres',
# 'qualification': {'id': 1,
#  'libelle': 'Sans qualification',
#  'libelle_abr': 'SQ'},
# 'is_bac_general': None,
# 'statuts_prioritaire': [{'id': 1,
#   'libelle': 'Personne éloignée du marché du travail (> 1 an)',
#   'libelle_abr': 'DELD',
#   'niveau': 99},
#  {'id': 2,
#   'libelle': 'Bénéficiaire de minima sociaux',
#   'libelle_abr': 'MINSOC',
#   'niveau': 99}],
# 'precision_status_prio': None,
# 'identifiant': 'NOM Prenom',
# 'identifiant_sans_accent': 'NOM Prenom',
# 'is_imported': None}

EMPLOYEE_MAPPING = {
    "label_id": "id",
    "geiq_id": "geiq_id",
    "last_name": "nom",
    "first_name": "prenom",
    "address_line_1": "adresse_ligne_1",
    "address_line_2": "adresse_ligne_2",
    "post_code": "adresse_code_postal",
    "city": "adresse_ville",
    "created_at": "date_creation",
    "title": "sexe",
    "birthdate": "date_naissance",
    "qualification": "qualification",
}


# EmployeeContract's other_data example:
# "date_debut": "2023-01-23T00:00:00+0100",
# "date_fin": "2023-11-26T00:00:00+0100",
# "heures_formation_prevue": None,
# "organisme_formation": "CENTRE RAYMOND BARD MIGRATION",
# "metier_prepare": "REGLEUR D ENROBES",
# "formation_complementaire_prevue": "",
# "is_multi_mad": False,
# "mad_nb_entreprises": None,
# "tarif_mad": 20.2,
# "is_remuneration_superieur_minima": False,
# "is_temps_plein": True,
# "state": 2,
# "date_fin_contrat": "2023-11-26T00:00:00+0100",
# "rupture": None,
# "is_present_in_examen": True,
# "is_qualification_obtenue": True,
# "metier_correspondant": "régleur d'enrobé",
# "formation_complementaire": "",
# "heures_formation_realisee": 462,
# "nature_contrat": {
#     "id": 1,
#     "libelle": "Contrat de professionnalisation",
#     "libelle_abr": "CPRO",
#     "groupe": "1",
#     "precision": False,
#     "formation": True,
# },
# "nature_contrat_precision": [],
# "nature_contrat_autre_precision": "",
# "secteur_activite": {"id": 11, "nom": "Non-concerné", "code": "NC"},
# "qualification_visee": {"id": 1, "libelle": "Non concerné", "libelle_abr": "NC"},
# "type_qualification_visee": {"id": 3, "libelle": "Positionnement de CCN", "libelle_abr": "CCN"},
# "type_qualification_obtenu": {"id": 3, "libelle": "Positionnement de CCN", "libelle_abr": "CCN"},
# "qualification_obtenu": [],
# "mode_validation": {"id": 1, "libelle": "Jury interne", "libelle_abr": "INTERNE"},
# "emploi_sorti": {"id": 1, "libelle": "Dans une entreprise adhérente", "libelle_abr": "ADH"},
# "emploi_sorti_precision": {"id": 1, "libelle": "CDI", "libelle_abr": "CDI"},
# "mise_en_situation_professionnelle_bool": False,
# "mise_en_situation_professionnelle_precision": "",
# "mise_en_situation_professionnelle": False,
# "emploi_sorti_precision_text": None,
# "signer_cadre_clause_insertion": False,
# "is_contrat_pro_experimental": True,
# "is_contrat_pro_associe_vae_inversee": False,
# "nb_heure_hebdo": None,
# "libre_cc_vise": "N1P2C170",
# "contrat_opco": "",
# "accompagnement_avant_contrat": None,
# "accompagnement_apres_contrat": None,
# "hors_alternance_precision": "",
# "modalite_formation": {"id": 2, "libelle": "Formation interne", "libelle_abr": "INTERNE"},
# "heures_accompagnement_vae_prevue": None,
# "heures_suivi_evaluation_competences_geiq_prevues": None,
# "code_rncp": "",
# "type_validation": {"id": 1, "libelle": "Totale", "libelle_abr": "TOTALE"},
# "is_refus_cdd_cdi": False,

CONTRACT_MAPPING = {
    "label_id": "id",
    "antenna_id": "antenne",
    "employee_id": "salarie",
}


def sync_employee_and_contracts(geiq_id):
    client = geiq_label.get_client()
    contract_infos = client.get_all_contracts(geiq_id)

    employee_infos = {}
    for contract_info in contract_infos:
        employee_info = contract_info["salarie"]
        for key in (
            "adresse_ligne_1",
            "adresse_ligne_2",
            "adresse_code_postal",
            "adresse_ville",
        ):
            employee_info[key] = normalize_null_values(employee_info[key])
        employee_info["date_creation"] = datetime.datetime.fromisoformat(employee_info["date_creation"])
        employee_info["date_naissance"] = datetime.date.fromisoformat(employee_info["date_naissance"][:10])
        employee_info["sexe"] = {"H": Title.M, "F": Title.MME}[employee_info["sexe"]]
        employee_info["qualification"] = employee_info["qualification"]["libelle_abr"]
        if employee_info["id"] in employee_infos:
            # Check consistency between contracts
            assert (
                employee_infos[employee_info["id"]] == employee_info
            ), f"{employee_info} != {employee_infos[employee_info['id']]}"
        else:
            employee_infos[employee_info["id"]] = employee_info
        contract_info["salarie"] = employee_info["id"]
        # If the contract is directly with the GEIQ, the antenne id is 0
        contract_info["antenne"] = contract_info["antenne"]["id"] or None

    employees_to_create = []
    employees_to_update = []
    employees_to_delete = []

    for item in yield_sync_diff(
        employee_infos.values(),
        "id",
        models.Employee.objects.all(),
        "label_id",
        [(col_key, db_key) for db_key, col_key in EMPLOYEE_MAPPING.items()],
    ):
        if item.kind in [DiffItemKind.ADDITION, DiffItemKind.EDITION]:
            employee = label_data_to_django(
                item.raw, mapping=EMPLOYEE_MAPPING, model=models.Employee, with_other_data=True
            )
            if item.kind == DiffItemKind.ADDITION:
                employees_to_create.append(employee)
            else:
                employee.pk = item.db_obj.pk
                employees_to_update.append(employee)
                print(item)
        elif item.kind == DiffItemKind.DELETION:
            employees_to_delete.add(item.key)

    print(f"Would create {len(employees_to_create)}")
    print(f"Would update {len(employees_to_update)}")
    print(f"Would delete {len(employees_to_delete)}")
    models.Employee.objects.bulk_create(employees_to_create)
    models.Employee.objects.bulk_update(
        employees_to_update, {db_key for db_key in EMPLOYEE_MAPPING if db_key != "label_id"}
    )

    contracts_to_create = []
    contracts_to_update = []
    contracts_to_delete = []

    for item in yield_sync_diff(
        contract_infos,
        "id",
        models.EmployeeContract.objects.all(),
        "label_id",
        [(col_key, db_key) for db_key, col_key in CONTRACT_MAPPING.items()],
    ):
        if item.kind in [DiffItemKind.ADDITION, DiffItemKind.EDITION]:
            employee = label_data_to_django(
                item.raw, mapping=CONTRACT_MAPPING, model=models.EmployeeContract, with_other_data=True
            )
            if item.kind == DiffItemKind.ADDITION:
                contracts_to_create.append(employee)
            else:
                employee.pk = item.db_obj.pk
                contracts_to_update.append(employee)
                print(item)
        elif item.kind == DiffItemKind.DELETION:
            contracts_to_delete.add(item.key)

    print(f"Would create {len(contracts_to_create)}")
    print(f"Would update {len(contracts_to_update)}")
    print(f"Would delete {len(contracts_to_delete)}")
    models.EmployeeContract.objects.bulk_create(contracts_to_create)
    models.EmployeeContract.objects.bulk_update(
        contracts_to_update, {db_key for db_key in CONTRACT_MAPPING if db_key != "label_id"}
    )
