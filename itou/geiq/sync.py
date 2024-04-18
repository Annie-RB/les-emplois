import datetime

from itou.utils.apis import geiq_label
from itou.utils.sync import DiffItemKind, yield_sync_diff

from . import models


def convert_ms_timestamp_to_datetime(nb_ms):
    if not nb_ms:
        return None
    return datetime.datetime.fromtimestamp(nb_ms / 1000)


def label_data_to_geiq(data):
    return models.GEIQLabelInfo(
        label_id=data.pop("id"),
        name=data.pop("nom"),
        created_at=convert_ms_timestamp_to_datetime(data.pop("date_creation")),
        siret=data.pop("siret") or "",
        address_line_1=data.pop("adresse"),
        address_line_2=data.pop("adresse2") or "",
        post_code=data.pop("cp"),
        city=data.pop("ville"),
        phone=data.pop("telephone") or "",
        email=data.pop("email") or "",
        ffgeiq_member=data.pop("is_adherent_ffgeiq"),
        other_data=data,
    )


def label_data_to_antenna(data):
    return models.GEIQAntenna(
        label_id=data.pop("id"),
        geiq_id=data.pop("geiq_id"),
        name=data.pop("nom"),
        created_at=convert_ms_timestamp_to_datetime(data.pop("date_creation")),
        siret=data.pop("siret") or "",
        address_line_1=data.pop("adresse"),
        address_line_2=data.pop("adresse2") or "",
        post_code=data.pop("cp"),
        city=data.pop("ville"),
        phone=data.pop("telephone") or "",
        email=data.pop("email") or "",
    )


def sync_geiqs_and_antennas():
    client = geiq_label.get_client()

    geiq_infos = client.get_all_geiq()
    print("All data downloaded")
    antenna_infos = []
    for geiq_info in geiq_infos:
        antenne_infos = geiq_info.pop("antennes")
        for antenne_info in antenne_infos:
            assert antenne_info["geiq_id"] == geiq_info["id"], antenne_info
        antenna_infos.extend(antenne_infos)

    geiqs_to_create = []
    geiqs_to_update = []
    geiqs_to_delete = []

    for item in yield_sync_diff(geiq_infos, "id", models.GEIQLabelInfo.objects.all(), "label_id", []):
        if item.kind in [DiffItemKind.ADDITION, DiffItemKind.EDITION]:
            geiq = label_data_to_geiq(item.raw)
            if item.kind == DiffItemKind.ADDITION:
                geiqs_to_create.append(geiq)
            else:
                geiq.pk = item.db_obj.pk
                geiqs_to_update.append(geiq)
        elif item.kind == DiffItemKind.DELETION:
            geiqs_to_delete.add(item.key)

    print(f"Would create {len(geiqs_to_create)}")
    print(f"Would update {len(geiqs_to_update)}")
    print(f"Would delete {len(geiqs_to_delete)}")
    models.GEIQLabelInfo.objects.bulk_create(geiqs_to_create)

    antennas_to_create = []
    antennas_to_update = []
    antennas_to_delete = []

    for item in yield_sync_diff(antenna_infos, "id", models.GEIQAntenna.objects.all(), "label_id", []):
        if item.kind in [DiffItemKind.ADDITION, DiffItemKind.EDITION]:
            antenna = label_data_to_antenna(item.raw)
            if item.kind == DiffItemKind.ADDITION:
                antennas_to_create.append(antenna)
            else:
                antenna.pk = item.db_obj.pk
                antennas_to_update.append(antenna)
        elif item.kind == DiffItemKind.DELETION:
            antennas_to_delete.add(item.key)

    print(f"Would create {len(antennas_to_create)}")
    print(f"Would update {len(antennas_to_update)}")
    print(f"Would delete {len(antennas_to_delete)}")
    models.GEIQAntenna.objects.bulk_create(antennas_to_create)
