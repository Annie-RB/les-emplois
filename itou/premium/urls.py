from django.urls import path
from django.views.generic import TemplateView

# Load plotly apps - this triggers their registration
import itou.premium.dash_apps  # noqa: F401
from itou.premium.views import dash_example_1_view


# https://docs.djangoproject.com/en/dev/topics/http/urls/#url-namespaces-and-included-urlconfs
# sapp_name = "premium"

urlpatterns = [
    path("demo-one", TemplateView.as_view(template_name="premium/demo_one.html"), name="demo-one"),
    path("demo-six", dash_example_1_view, name="demo-six"),
]
