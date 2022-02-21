from datetime import datetime

from django.contrib.postgres.search import TrigramSimilarity
from django.db.models import Q
from django.http import JsonResponse
from django.template.defaultfilters import slugify

from itou.asp.models import Commune
from itou.cities.models import City
from itou.jobs.models import Appellation
from itou.siaes.models import SiaeJobDescription
from itou.utils.swear_words import get_city_swear_words_slugs


def cities_autocomplete(request):
    """
    Returns JSON data compliant with the jQuery UI Autocomplete Widget:
    https://api.jqueryui.com/autocomplete/#option-source
    """

    term = request.GET.get("term", "").strip()
    cities = []

    if term and slugify(term) not in get_city_swear_words_slugs():
        cities = (
            City.objects.annotate(similarity=TrigramSimilarity("name", term))
            .filter(similarity__gt=0.1)
            .order_by("-similarity")
        )
        cities = cities[:12]

        cities = [{"value": city.display_name, "slug": city.slug} for city in cities]

    return JsonResponse(cities, safe=False)


def jobs_autocomplete(request):
    """
    Returns JSON data compliant with the jQuery UI Autocomplete Widget:
    https://api.jqueryui.com/autocomplete/#option-source
    """

    term = request.GET.get("term", "").strip()
    siae_id = request.GET.get("siae_id", "").strip()
    appellations = []

    # Fetch excluded codes:
    # SIAE already have job descriptions with these codes.
    excluded_codes = (
        SiaeJobDescription.objects.filter(siae__id=siae_id)
        .select_related("appellation", "siae")
        .values_list("appellation__code", flat=True)
    )

    if term:
        appellations = [
            {
                "value": f"{appellation.name} ({appellation.rome.code})",
                "code": appellation.code,
                "rome": appellation.rome.code,
                "name": appellation.name,
            }
            for appellation in Appellation.objects.autocomplete(term, codes_to_exclude=excluded_codes, limit=10)
        ]

    return JsonResponse(appellations, safe=False)


def communes_autocomplete(request):
    """
    Autocomplete endpoint for INSEE communes (ASP ref. files)

    Slight variation : a `date` parameter is sent with search term
    in order to get valid INSEE codes (with this date within a period between
    commune.start_date and commune.end_date)

    Returns JSON data compliant with the jQuery UI Autocomplete Widget:
    https://api.jqueryui.com/autocomplete/#option-source
    """
    communes = []
    term = request.GET.get("term", "").strip()

    try:
        dt = datetime.fromisoformat(request.GET.get("date", ""))
    except ValueError:
        # Can't extract date in ISO format: use today as fallback
        dt = datetime.now()

    if term:
        communes = (
            Commune.objects.filter(start_date__lte=dt)
            .filter(Q(end_date=None) | Q(end_date__gt=dt))
            .annotate(similarity=TrigramSimilarity("name", term))
            .filter(similarity__gt=0.1)
            .order_by("-similarity")
        )
        communes = [
            {
                "value": f"{commune.name} ({commune.department_code})",
                "code": commune.code,
                "department": commune.department_code,
            }
            for commune in communes[:12]
        ]

    return JsonResponse(communes, safe=False)
