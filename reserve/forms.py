from django import forms

from reserve.models import Bon, Room, Other, Reserve


class RoomCreateForm(forms.ModelForm):
    name = forms.CharField(label="nom de la chambre")
    description = forms.CharField(label="détails de la chambre", required=False)

    class Meta:
        model = Room
        fields = (
            "name",
            "description",
        )


class ReserveCreateForm(forms.ModelForm):
    start_date = forms.DateField(
        label="date de début",
        widget=forms.DateInput(
            format=("%Y-%m-%d"),
            attrs={
                "placeholder": "Select a date",
                "type": "date",
            },
        ),
    )
    end_date = forms.DateField(
        label="date de fin",
        widget=forms.DateInput(
            format=("%Y-%m-%d"),
            attrs={
                "placeholder": "Select a date",
                "type": "date",
            },
        ),
    )
    client = forms.CharField(label="Nom du client", max_length=255)
    price = forms.DecimalField(label="montant total")

    class Meta:
        model = Reserve
        fields = (
            "start_date",
            "end_date",
            "client",
            "price",
        )


class PdfOtherCreateForm(forms.ModelForm):
    name = forms.CharField()
    price = forms.DecimalField()

    class Meta:
        model = Other
        fields = (
            "name",
            "price",
        )


class BonForm(forms.ModelForm):
    description = forms.CharField(label="Desination")
    price = forms.CharField(label="Prix", required=False)

    class Meta:
        model = Bon
        fields = (
            "description",
            "price",
        )
