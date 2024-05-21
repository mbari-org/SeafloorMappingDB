from django import forms
from django_filters import (
    FilterSet,
    CharFilter,
    BooleanFilter,
    ChoiceFilter,
    ModelChoiceFilter,
)
from smdb.models import Mission, Expedition, Compilation

from django.forms.widgets import TextInput


class MissionFilter(FilterSet):
    name = CharFilter(
        field_name="name",
        lookup_expr="icontains",
        label="",
        widget=TextInput(attrs={"placeholder": "Name contains..."}),
    )
    expedition__name = CharFilter(
        field_name="expedition__name",
        lookup_expr="icontains",
        label="",
        widget=TextInput(attrs={"placeholder": "Expedition name contains..."}),
    )
    status = ChoiceFilter(
        field_name="status",
        choices=Mission.STATUS_CHOICES,
        label="",
        empty_label="--- status ---",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    patch_test = BooleanFilter(
        field_name="patch_test",
        label="Patch Test",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )

    class Meta:
        model = Mission
        fields = ["name", "expedition__name", "status", "patch_test"]


class ExpeditionFilter(FilterSet):
    name = CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Expedition
        fields = [
            "name",
        ]


class CompilationFilter(FilterSet):
    name = CharFilter(field_name="name", lookup_expr="icontains")
    has_thumbnail = BooleanFilter(
        field_name="thumbnail_filename",
        lookup_expr="isnull",
        exclude=True,
        label="Has Thumbnail Image",
    )
    has_missions = BooleanFilter(
        field_name="missions", lookup_expr="isnull", exclude=True, label="Has Missions"
    )

    class Meta:
        model = Compilation
        fields = ["name"]
