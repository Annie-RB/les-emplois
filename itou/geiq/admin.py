from django.contrib import admin

from ..utils.admin import ItouModelAdmin
from . import models


class ReadonlyMixin:

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(models.GEIQLabelInfo)
class GEIQLabelInfoAdmin(ReadonlyMixin, ItouModelAdmin):
    list_display = (
        "pk",
        "name",
    )


@admin.register(models.Employee)
class EmployeeAdmin(ReadonlyMixin, ItouModelAdmin):
    list_display = (
        "pk",
        "geiq",
        "last_name",
        "first_name",
    )


@admin.register(models.EmployeeContract)
class EmployeeContractAdmin(ReadonlyMixin, ItouModelAdmin):
    list_display = (
        "pk",
        "employee",
    )
