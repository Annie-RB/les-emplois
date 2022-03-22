import logging

from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, TokenAuthentication

from itou.employee_record.models import EmployeeRecord, EmployeeRecordUpdateNotification
from itou.employee_record.serializers import EmployeeRecordUpdateNotificationSerializer
from itou.job_applications.models import JobApplication

from .perms import EmployeeRecordAPIPermission
from .serializers import DummyEmployeeRecordSerializer, EmployeeRecordAPISerializer


logger = logging.getLogger("api_drf")


class DummyEmployeeRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    # API fiches salarié (FAKE)

    Cette API retourne des données de fiches salarié factices et identiques
    à des fins de test pour les éditeurs de logiciels.
    """

    # Above doc section is in french for Swagger / OAS auto doc generation

    serializer_class = DummyEmployeeRecordSerializer
    authentication_classes = [TokenAuthentication, SessionAuthentication]
    # By default, permission class is IsAuthenticated

    def get_queryset(self):
        """
        Return the same 25 job applications whatever the user.
        The DummyEmployeeRecordSerializer will replace these objects with raw randomized jsons.
        25 is slightly more than the default page size (20) so that pagination can be tested.
        Order by pk to solve pagination warning.
        """
        return JobApplication.objects.order_by("pk")[:25]


class AbstractEmployeeRecordViewSet(viewsets.ReadOnlyModelViewSet):

    # Possible authentication frameworks:
    # - token auth: for external access / real world use case
    # - session auth: for dev context and browseable API
    authentication_classes = [TokenAuthentication, SessionAuthentication]

    # Additional / custom permission classes:
    # Enforce the default one (IsAuthenticated)
    permission_classes = [EmployeeRecordAPIPermission]


class EmployeeRecordViewSet(AbstractEmployeeRecordViewSet):
    """
    # API fiches salarié

    Cette API retourne la liste des fiches salarié saisies par les SIAE :

    - dans l'état `PROCESSED` (par défaut)
    - pour toutes les embauches / candidatures des SIAE liées au token d'identification
    - classées par date de création et date de mise à jour (plus récent au plus ancien)

    Il est également possible d'obtenir le détail d'une fiche salarié par son
    identifiant (dans les mêmes conditions d'autorisation que pour la liste complète)

    # Permissions

    L'utilisation externe de cette API nécessite l'utilisation d'un token d'autorisation
    (voir le endpoint `auth-token`).

    L'API peut également être utilisée dans un navigateur :

    - seulement dans un environnement de développement
    - si l'utilisateur connecté est membre d'une ou plusieurs SIAE éligible aux fiches salarié

    # Paramètres
    Les paramètres suivants sont utilisables en paramètres de requête (query string):

    ## `status` : statut des fiches salarié
    Ce paramètre est un tableau permettant de filtrer les fiches retournées par leur statut

    Les valeurs possibles pour ce paramètre sont :

    - `NEW` : nouvelle fiche en cours de saisie,
    - `READY` : la fiche est prête à être transmise à l'ASP,
    - `SENT` : la fiche a été transmise et est en attente de traitement,
    - `PROCESSED` : la fiche a correctement été intégrée par l'ASP,
    - `REJECTED` : la fiche est retournée en erreur après transmission.

    ### Exemples
    - ajouter `?status=NEW` à l'URL pour les nouvelles fiches.
    - ajouter `?status=NEW&status=READY` pour les nouvelles fiches et celles prêtes pour la transmission.

    """

    # Above doc section is in french for Swagger / OAS auto doc generation

    # If no queryset class parameter is given (f.i. overidding)
    # a `basename` parameter must be set on the router (see local `urls.py` file)
    # See: https://www.django-rest-framework.org/api-guide/routers/

    serializer_class = EmployeeRecordAPISerializer

    def get_queryset(self):
        # We only get to this point if permissions are OK
        queryset = EmployeeRecord.objects.full_fetch()

        # Get (registered) query parameters filters
        queryset = self._filter_by_query_params(self.request, queryset)

        # Employee record API will return objects related to
        # all SIAE memberships of authenticated user.
        # There's something similar in context processors, but:
        # - ctx processors are called AFTER this
        # - and only when rendering a template
        siaes = self.request.user.siae_set.filter(
            siaemembership__is_active=True, siaemembership__is_admin=True
        ).active_or_in_grace_period()

        try:
            return queryset.filter(job_application__to_siae__in=siaes).order_by("-created_at", "-updated_at")
        finally:
            # Tracking is currently done via user-agent header
            logger.info(
                "User-Agent: %s",
                self.request.headers.get("User-Agent"),
            )

    def _filter_by_query_params(self, request, queryset):
        """
        Register query parameters result filtering:
        - only using employee record `status` is available for now.
        - `status` query param can be an array of value.
        """
        params = request.query_params

        if status := params.getlist("status", ""):
            status_filter = [s.upper() for s in status]

            return queryset.filter(status__in=status_filter).order_by("-created_at")

        # => Add as many params as necessary here (PASS IAE number, SIRET, fuzzy name ...)

        # Default queryset without params
        return queryset.processed()


class EmployeeRecordUpdateNotificationViewSet(AbstractEmployeeRecordViewSet):
    queryset = EmployeeRecordUpdateNotification.objects.all()
    serializer_class = EmployeeRecordUpdateNotificationSerializer
