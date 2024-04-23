import enum

from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from itou.geiq.models import Employee, EmployeeContract, GEIQLabelInfo
from itou.geiq.sync import sync_employee_and_contracts
from itou.utils.pagination import pager


class InfoType(enum.StrEnum):
    PERSONAL_INFORMATION = "personal-information"
    JOB_APPLICATION = "job-application"
    SUPPORT = "support"
    CONTRACT = "contract"
    EXIT = "exit"

    # Otherwise Django will detect InfoType as callable and access to individual values does not work
    do_not_call_in_templates = enum.nonmember(True)


@login_required
@require_GET
def assessment_info(request, geiq_pk, year=None, template_name="geiq/assessment_info.html"):
    if geiq_pk not in {org.pk for org in request.organizations}:
        raise Http404("GEIQ inconnue")
    geiq_label_info = GEIQLabelInfo.objects.filter(company_id=geiq_pk).first()
    context = {
        "geiq_pk": geiq_pk,
        "InfoType": InfoType,
        "label_info": geiq_label_info,
    }
    return render(request, template_name, context)


@login_required
@require_GET
def employee_list(request, geiq_pk, info_type, year=None):
    try:
        info_type = InfoType(info_type)
    except ValueError:
        raise Http404("Type de donnée inconnu")
    if geiq_pk not in {org.pk for org in request.organizations}:
        raise Http404("GEIQ inconnue")
    geiq_label_info = GEIQLabelInfo.objects.filter(company_id=geiq_pk).first()

    match info_type:
        case InfoType.PERSONAL_INFORMATION:
            queryset = Employee.objects.filter(geiq__company_id=geiq_pk).order_by("last_name", "first_name")
            template_name = "geiq/employee_personal_information_list.html"
        case InfoType.JOB_APPLICATION:
            queryset = EmployeeContract.objects.filter(employee__geiq__company_id=geiq_pk).order_by(
                "employee__last_name", "employee__first_name"
            )
            template_name = "geiq/employee_job_application_list.html"
        case InfoType.SUPPORT:
            queryset = EmployeeContract.objects.filter(employee__geiq__company_id=geiq_pk).order_by(
                "employee__last_name", "employee__first_name"
            )
            template_name = "geiq/employee_support_list.html"
        case InfoType.CONTRACT:
            queryset = EmployeeContract.objects.filter(employee__geiq__company_id=geiq_pk).order_by(
                "employee__last_name", "employee__first_name"
            )
            template_name = "geiq/employee_contract_list.html"
        case InfoType.EXIT:
            queryset = EmployeeContract.objects.filter(employee__geiq__company_id=geiq_pk).order_by(
                "employee__last_name", "employee__first_name"
            )
            template_name = "geiq/employee_exit_list.html"

    context = {
        "active_tab": info_type,
        "accompanied_nb": None,
        "accompanied_more_than_3_months_nb": None,
        "eligible_for_aid_employee_nb": None,
        "potential_aid_of_814_nb": None,
        "potential_aid_of_1400_nb": None,
        "potential_aid_amount": None,
        "data_page": pager(queryset, request.GET.get("page"), items_per_page=50),
        "InfoType": InfoType,
        "label_info": geiq_label_info,
    }
    return render(request, template_name, context)


@login_required
@require_POST
def label_sync(request, geiq_pk):
    if geiq_pk not in {org.pk for org in request.organizations}:
        raise Http404("GEIQ inconnue")
    geiq_label_info = GEIQLabelInfo.objects.filter(company_id=geiq_pk).select_for_update().first()

    if not geiq_label_info:
        raise Http404("GEIQ inconnue de Label")
    sync_employee_and_contracts(geiq_label_info.label_id)
    geiq_label_info.refresh_from_db()
    context = {
        "label_info": geiq_label_info,
        "oob_swap": True,
    }
    return render(request, "geiq/includes/last_synced_at.html", context)
