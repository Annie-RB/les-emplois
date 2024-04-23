from django.urls import path

from itou.www.geiq_views import views


app_name = "geiq"

urlpatterns = [
    path(
        "<int:geiq_pk>/label-sync",
        views.label_sync,
        name="label_sync",
    ),
    path(
        "<int:geiq_pk>/assessment",
        views.assessment_info,
        name="assessment_info",
    ),
    path(
        "<int:geiq_pk>/assessment/<int:year>",
        views.assessment_info,
        name="assessment_info",
    ),
    path(
        "<int:geiq_pk>/employees/<slug:info_type>",
        views.employee_list,
        name="employee_list",
    ),
    path(
        "<int:geiq_pk>/employees/<slug:info_type>/<int:year>",
        views.employee_list,
        name="employee_list",
    ),
]
