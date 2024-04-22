from django.urls import path

from itou.www.geiq_views import views


app_name = "geiq"

urlpatterns = [
    path("employees/<int:geiq_pk>", views.employees, name="employees"),
    path("employees/<int:geiq_pk>/<int:year>", views.employees, name="employees"),
]
