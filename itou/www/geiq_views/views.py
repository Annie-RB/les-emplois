from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.http import require_GET


@login_required
@require_GET
def employees(request, geiq_pk, year=None, template_name="geiq/employees_list.html"):
    context = {}
    return render(request, template_name, context)
