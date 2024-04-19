import enum

import httpx
from django.conf import settings


API_TIMEOUT_SECONDS = 5.0


class LabelCommand(enum.StrEnum):
    Salarie = "Salarie"
    SalarieContrat = "SalarieContrat"
    SalariePreQualification = "SalariePreQualification"
    GeiqFFGeiq = "GeiqFFGeiq"
    Adherent = "Adherent"
    Prescripteur = "Prescripteur"
    GeiqPrestation = "GeiqPrestation"
    Accompagnement = "Accompagnement"
    Preremplissage = "Preremplissage"
    DecompteHeures = "DecompteHeures"
    LignesCompte = "LignesCompte"
    CompteResultat = "CompteResultat"
    EquipeAdministrative = "EquipeAdministrative"


class LabelApiClient:
    def __init__(self, base_url: str, token: str):
        self.client = httpx.Client(
            base_url=base_url,
            headers={"Authorization": token},
            timeout=API_TIMEOUT_SECONDS,
        )

    def _command(self, command, **params):
        command = LabelCommand(command)
        response = self.client.get(
            f"rest/{command}",
            params=params,
        )
        response.raise_for_status()
        response_data = response.json()
        if response_data.get("status") != "Success":
            raise ValueError(response_data.get("Status"))
        return response_data["result"]

    def get_geiq_by_siret(self, siret):
        assert siret.isdigit(), siret
        return self._command(LabelCommand.GeiqFFGeiq, where=f"geiq.siret,=,{siret}")

    def get_all_geiq(self, *, page_size=50):
        data = []
        p = 1
        while new_values := self._command(LabelCommand.GeiqFFGeiq, n=page_size, p=p):
            data.extend(new_values)
            p += 1
        return data

    def get_all_contracts(self, geiq_id, *, page_size=50):
        data = []
        p = 1
        while new_values := self._command(
            LabelCommand.SalarieContrat, join="salariecontrat.salarie,s", where=f"s.geiq,=,{geiq_id}", n=page_size, p=p
        ):
            data.extend(new_values)
            p += 1
        return data


def get_client():
    return LabelApiClient(
        base_url=settings.API_GEIQ_LABEL_BASE_URL,
        token=settings.API_GEIQ_LABEL_TOKEN,
    )
