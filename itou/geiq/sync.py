import datetime

from itou.utils.apis import geiq_label
from itou.utils.sync import DiffItemKind, yield_sync_diff

from . import models


def convert_ms_timestamp_to_datetime(nb_ms):
    if not nb_ms:
        return None
    return datetime.datetime.fromtimestamp(nb_ms / 1000)


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
