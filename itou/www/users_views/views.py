from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import DetailView

from itou.gps.models import FollowUpGroupMembership
from itou.users.models import User


class UserDetailsView(LoginRequiredMixin, DetailView):
    model = User
    queryset = User.objects.select_related("follow_up_group", "jobseeker_profile").prefetch_related(
        "follow_up_group__memberships"
    )
    template_name = "users/details.html"
    slug_field = "public_id"
    slug_url_kwarg = "public_id"
    context_object_name = "user"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["gps_memberships"] = (
            FollowUpGroupMembership.objects.filter(follow_up_group=self.object.follow_up_group)
            .filter(is_active=True)
            .order_by("-is_referent")
            .select_related("follow_up_group", "member")
        )

        context["profile"] = self.object.jobseeker_profile

        context["can_view_personal_information"] = self.request.user.can_view_personal_information(self.object)

        context["breadcrumbs"] = {
            "Mes bénéficiaires": reverse("gps:my_groups"),
            f"Fiche de {self.object.get_full_name()}": reverse(
                "users:details", kwargs={"public_id": self.object.public_id}
            ),
        }

        return context
