from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from itou.gps.models import FollowUpGroup
from itou.www.gps.forms import GpsUserSearchForm


@login_required
def my_groups(request, template_name="gps/my_groups.html"):

    current_user = request.user
    groups = (
        FollowUpGroup.objects.filter(members=current_user)
        .select_related("beneficiary")
        .prefetch_related("members")
        .all()
    )

    breadcrumbs = {
        "Mes groupes de suivi": reverse("gps:my_groups"),
    }

    context = {
        "breadcrumbs": breadcrumbs,
        "groups": groups,
    }

    return render(request, template_name, context)


@login_required
def join_group(request, template_name="gps/join_group.html"):

    form = GpsUserSearchForm(data=request.POST or None)

    my_groups_url = reverse("gps:my_groups")

    if request.method == "POST" and form.is_valid():
        return HttpResponseRedirect(my_groups_url)

    breadcrumbs = {
        "Mes groupes de suivi": my_groups_url,
        "Rejoindre un groupe de suivi": reverse("gps:join_group"),
    }

    context = {"breadcrumbs": breadcrumbs, "form": form, "reset_url": my_groups_url}

    return render(request, template_name, context)
