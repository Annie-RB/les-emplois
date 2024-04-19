import datetime

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
    "created_at": lambda data: convert_ms_timestamp_to_datetime(data["date_creation"]),
    "siret": "siret",
    "address_line_1": "adresse",
    "address_line_2": "adresse2",
    "post_code": "cp",
    "city": "ville",
    "phone": "telephone",
    "email": "email",
    "ffgeiq_member": "is_adherent_ffgeiq",
}


def label_data_to_geiq(data):
    geiq_data = {}
    other_data = dict(data)
    for db_key, label_key in GEIQ_MAPPING.items():
        if db_key == "created_at":
            geiq_data[db_key] = label_key(data)
            other_data.pop("date_creation")
        else:
            geiq_data[db_key] = data[label_key]
            other_data.pop(label_key)
    geiq_data["other_data"] = other_data
    return models.GEIQLabelInfo(**geiq_data)


ANTENNA_MAPPING = {
    "label_id": "id",
    "geiq_id": "geiq_id",
    "name": "nom",
    "created_at": lambda data: convert_ms_timestamp_to_datetime(data["date_creation"]),
    "siret": "siret",
    "address_line_1": "adresse",
    "address_line_2": "adresse2",
    "post_code": "cp",
    "city": "ville",
    "phone": "telephone",
    "email": "email",
}


def label_data_to_antenna(data):
    antenna_data = {}
    for db_key, label_key in ANTENNA_MAPPING.items():
        if db_key == "created_at":
            antenna_data[db_key] = label_key(data)
        else:
            antenna_data[db_key] = data[label_key]
    return models.GEIQAntenna(**antenna_data)


def normalize_null_values(value):
    if value is None:
        return ""
    return value


def sync_geiqs_and_antennas():
    client = geiq_label.get_client()

    geiq_infos = client.get_all_geiq()
    print("All data downloaded")
    antenna_infos = []
    for geiq_info in geiq_infos:
        for key in (
            "siret",
            "telephone",
            "email",
            "adresse2",
        ):
            geiq_info[key] = normalize_null_values(geiq_info[key])
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
            geiq = label_data_to_geiq(item.raw)
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
            antenna = label_data_to_antenna(item.raw)
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


# 'date_creation': '2017-03-21T00:00:00+0100',
# 'numero': '123',
# 'date_naissance': '1970-01-01T00:00:00+0100',
# 'sexe': 'H',
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
    "created_at": lambda data: convert_ms_timestamp_to_datetime(data["date_creation"]),
}


def label_data_to_employee(data):
    employee_data = {}
    for db_key, label_key in ANTENNA_MAPPING.items():
        if db_key == "created_at":
            employee_data[db_key] = label_key(data)
        else:
            employee_data[db_key] = data[label_key]
    return models.Employee(**employee_data)


def sync_employee_and_contracts(geiq_id):
    client = geiq_label.get_client()

    contract_infos = client.get_all_contracts(geiq_id)
    employee_infos = {}
    for contract_info in contract_infos:
        for key in (
            "siret",
            "telephone",
            "email",
            "adresse2",
        ):
            contract_info[key] = normalize_null_values(contract_info[key])
        employee_info = contract_info["salarie"]
        if employee_info["id"] in employee_infos:
            # Check consistency between contracts
            assert employee_infos[employee_info["id"]] == employee_info
        else:
            employee_infos[employee_info["id"]] = employee_info
        employee_info["salarie"] = employee_info["id"]
        contract_infos.extend(contract_infos)

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
            geiq = label_data_to_geiq(item.raw)
            if item.kind == DiffItemKind.ADDITION:
                employees_to_create.append(geiq)
            else:
                geiq.pk = item.db_obj.pk
                employees_to_update.append(geiq)
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
