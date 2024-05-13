import datetime

from django.utils import timezone

from itou.companies.models import Company, CompanyKind
from itou.users.enums import Title
from itou.utils.apis import geiq_label
from itou.utils.sync import DiffItemKind, yield_sync_diff

from . import models


def convert_ms_timestamp_to_datetime(nb_ms):
    if not nb_ms:
        return None
    return datetime.datetime.fromtimestamp(nb_ms / 1000, tz=datetime.timezone.utc)


def convert_iso_datetime_to_date(iso_datetime):
    # We receive '1970-01-01T00:00:00+0100' or '2022-09-19T00:00:00+0200' values for dates
    return datetime.date.fromisoformat(iso_datetime[:10])


def normalize_null_values(value):
    if value is None:
        return ""
    return value


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


def sync_to_db(api_data, db_queryset, *, model, mapping, with_other_data):
    obj_to_create = []
    obj_to_update = []
    obj_to_delete = []

    for item in yield_sync_diff(
        api_data,
        "id",
        db_queryset,
        "label_id",
        [(col_key, db_key) for db_key, col_key in mapping.items()],
    ):
        if item.kind in [DiffItemKind.ADDITION, DiffItemKind.EDITION]:
            obj = label_data_to_django(item.raw, mapping=mapping, model=model, with_other_data=with_other_data)
            if item.kind == DiffItemKind.ADDITION:
                obj_to_create.append(obj)
            else:
                obj.pk = item.db_obj.pk
                obj_to_update.append(obj)
        elif item.kind == DiffItemKind.DELETION:
            obj_to_delete.append(item.key)

    print(f"Will create {len(obj_to_create)} {model._meta.verbose_name}")
    print(f"Will update {len(obj_to_update)} {model._meta.verbose_name}")
    print(f"Would delete {len(obj_to_delete)} {model._meta.verbose_name}")
    model.objects.bulk_create(obj_to_create)
    model.objects.bulk_update(obj_to_update, {db_key for db_key in mapping if db_key != "label_id"})


def sync_geiqs_and_antennas():
    siret_to_company = {
        company.siret: company for company in Company.objects.filter(kind=CompanyKind.GEIQ).exclude(siret="")
    }
    client = geiq_label.get_client()
    geiq_infos = client.get_all_geiq()

    antenna_label_infos = []
    geiq_label_infos = []
    for geiq_info in geiq_infos:
        for key in (
            "siret",
            "telephone",
            "email",
            "adresse2",
        ):
            geiq_info[key] = normalize_null_values(geiq_info[key])
        if not geiq_info["siret"]:
            print(f"Ignoring geiq={geiq_info['nom']} without SIRET")
            continue
        if geiq_info["siret"] not in siret_to_company:
            print(f"Ignoring geiq={geiq_info['nom']} with unknown SIRET={geiq_info['siret']}")
            continue
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
        geiq_label_infos.append(geiq_info)
        antenna_label_infos.extend(antenne_infos)

    geiqs_to_create = []
    geiqs_to_update = []
    geiqs_to_delete = []

    for item in yield_sync_diff(
        geiq_label_infos,
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
                # This line prevents the use of sync_to_db utility
                geiq.company = siret_to_company[geiq.siret]
                geiqs_to_create.append(geiq)
            else:
                geiq.pk = item.db_obj.pk
                geiqs_to_update.append(geiq)
                print(item)
        elif item.kind == DiffItemKind.DELETION:
            geiqs_to_delete.add(item.key)

    print(f"Will create {len(geiqs_to_create)} GEIQ")
    print(f"Will update {len(geiqs_to_update)} GEIQ")
    print(f"Would delete {len(geiqs_to_delete)} GEIQ")
    models.GEIQLabelInfo.objects.bulk_create(geiqs_to_create)
    models.GEIQLabelInfo.objects.bulk_update(
        geiqs_to_update, {db_key for db_key in GEIQ_MAPPING if db_key != "label_id"}
    )

    sync_to_db(
        antenna_label_infos,
        models.GEIQAntenna.objects.all(),
        model=models.GEIQAntenna,
        mapping=ANTENNA_MAPPING,
        with_other_data=False,
    )


# Employee's other_data example:
# 'numero': '123',
# 'prescripteur': {'id': 13, 'libelle': 'Autres', 'libelle_abr': 'AUTRE'},
# 'prescripteur_autre': '1 Autres',
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
    "prescriber_type": "prescripteur",
}


# EmployeeContract's other_data example:
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
# "rupture": None,
# "is_present_in_examen": True,
# "is_qualification_obtenue": True,
# "metier_correspondant": "régleur d'enrobé",
# "formation_complementaire": "",
# "heures_formation_realisee": 462,
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
    "start_at": "date_debut",
    "planned_end_at": "date_fin",
    "end_at": "date_fin_contrat",
    "nb_hours_per_week": "nb_heure_hebdo",
    "contract_type": "nature_contrat",
}


#  'information_complementaire_contrat': None,
#  'autre_type_prequalification_action': None,

PREQUALIFICATION_MAPPING = {
    "label_id": "id",
    "employee_id": "salarie",
    "start_at": "date_debut",
    "end_at": "date_fin",
    "action": "action_pre_qualification",
    "training_hours_nb": "nombre_heure_formation",
}


def _cleanup_employee_info(employee_info):
    for key in (
        "adresse_ligne_1",
        "adresse_ligne_2",
        "adresse_code_postal",
        "adresse_ville",
    ):
        employee_info[key] = normalize_null_values(employee_info[key])
    employee_info["date_creation"] = datetime.datetime.fromisoformat(employee_info["date_creation"])
    employee_info["date_naissance"] = convert_iso_datetime_to_date(employee_info["date_naissance"])
    employee_info["sexe"] = {"H": Title.M, "F": Title.MME}[employee_info["sexe"]]
    employee_info["qualification"] = employee_info["qualification"]["libelle_abr"]
    employee_info["prescripteur"] = employee_info["prescripteur"]["libelle_abr"]


def sync_employee_and_contracts(geiq_id):
    client = geiq_label.get_client()
    if client is None:
        raise ValueError("Missing configuration")
    contract_infos = client.get_all_contracts(geiq_id)
    prequalification_infos = client.get_all_prequalifications(geiq_id)

    employee_infos = {}
    for contract_info in contract_infos:
        employee_info = contract_info["salarie"]
        _cleanup_employee_info(employee_info)
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
        contract_info["date_debut"] = convert_iso_datetime_to_date(contract_info["date_debut"])
        contract_info["date_fin"] = convert_iso_datetime_to_date(contract_info["date_fin"])
        contract_info["date_fin_contrat"] = (
            convert_iso_datetime_to_date(contract_info["date_fin_contrat"])
            if contract_info["date_fin_contrat"]
            else None
        )
        contract_info["nature_contrat"] = contract_info["nature_contrat"]["libelle_abr"]

    for prequalification_info in prequalification_infos:
        employee_info = prequalification_info["salarie"]
        _cleanup_employee_info(employee_info)
        if employee_info["id"] in employee_infos:
            # Check consistency between contracts & prequalifications
            assert (
                employee_infos[employee_info["id"]] == employee_info
            ), f"{employee_info} != {employee_infos[employee_info['id']]}"
        else:
            employee_infos[employee_info["id"]] = employee_info
        prequalification_info["salarie"] = employee_info["id"]
        prequalification_info["date_debut"] = convert_iso_datetime_to_date(prequalification_info["date_debut"])
        prequalification_info["date_fin"] = convert_iso_datetime_to_date(prequalification_info["date_fin"])
        prequalification_info["action_pre_qualification"] = prequalification_info["action_pre_qualification"][
            "libelle_abr"
        ]

    sync_to_db(
        employee_infos.values(),
        models.Employee.objects.filter(geiq__label_id=geiq_id).all(),
        model=models.Employee,
        mapping=EMPLOYEE_MAPPING,
        with_other_data=True,
    )

    sync_to_db(
        contract_infos,
        models.EmployeeContract.objects.filter(employee__geiq__label_id=geiq_id).all(),
        model=models.EmployeeContract,
        mapping=CONTRACT_MAPPING,
        with_other_data=True,
    )

    sync_to_db(
        prequalification_infos,
        models.EmployeePrequalification.objects.filter(employee__geiq__label_id=geiq_id).all(),
        model=models.EmployeePrequalification,
        mapping=PREQUALIFICATION_MAPPING,
        with_other_data=True,
    )

    models.GEIQLabelInfo.objects.filter(label_id=geiq_id).update(last_synced_at=timezone.now())
