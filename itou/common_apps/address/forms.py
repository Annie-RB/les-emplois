import django.forms as forms
from django.urls import reverse_lazy
from django.utils.text import format_lazy

from itou.cities.models import City
from itou.users.models import User
from itou.utils.widgets import RemoteAutocompleteSelect2Widget


class OptionalAddressFormMixin(forms.Form):
    """
    Form mixin that allows to enter an optional address.
    """

    city = forms.ModelChoiceField(
        queryset=City.objects,
        label="Ville",
        required=False,
        widget=RemoteAutocompleteSelect2Widget(
            attrs={
                "data-ajax--url": format_lazy("{}?select2=", reverse_lazy("autocomplete:cities")),
                "data-ajax--cache": "true",
                "data-ajax--type": "GET",
                "data-minimum-input-length": 2,
                "data-placeholder": "Nome de la ville",
            },
        ),
    )

    address_line_1 = forms.CharField(
        required=False,
        max_length=User._meta.get_field("address_line_1").max_length,
        label="Adresse",
    )

    address_line_2 = forms.CharField(
        required=False,
        max_length=User._meta.get_field("address_line_2").max_length,
        label="Complément d'adresse",
    )

    post_code = forms.CharField(
        required=False,
        max_length=User._meta.get_field("post_code").max_length,
        label="Code postal",
    )

    def clean(self):
        cleaned_data = super().clean()

        # Basic check of address fields.
        addr1, addr2, post_code, city = (
            cleaned_data["address_line_1"],
            cleaned_data["address_line_2"],
            cleaned_data["post_code"],
            cleaned_data["city"],
        )

        valid_address = all([addr1, post_code, city])
        empty_address = not any([addr1, addr2, post_code, city])
        if not empty_address and not valid_address:
            if not addr1:
                self.add_error("address_line_1", "Adresse : ce champ est obligatoire.")
            if not post_code:
                self.add_error("post_code", "Code postal : ce champ est obligatoire.")
            if not city:
                self.add_error("city", "Ville : ce champ est obligatoire.")


class MandatoryAddressFormMixin(OptionalAddressFormMixin):
    """
    Form mixin that requires an address.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["address_line_1"].required = True
        self.fields["post_code"].required = True
        self.fields["city"].required = True

    def clean(self):
        if self.errors:
            return  # An error here means that some required fields were left blank.
        super().clean()
