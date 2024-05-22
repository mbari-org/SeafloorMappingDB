from django import forms
from django_filters import (
    FilterSet,
    CharFilter,
    BooleanFilter,
    ChoiceFilter,
    ModelChoiceFilter,
)
from smdb.models import Mission, Expedition, Compilation

from django.forms.widgets import TextInput, 


class MissionFilter(FilterSet):
    name = CharFilter(
        field_name="name",
        lookup_expr="icontains",
        label="",
        widget=TextInput(attrs={"placeholder": "Name contains..."}),
    )
    region_name = ChoiceFilter(
        field_name="region_name",
        choices=[
            (m, m)
            for m in Mission.objects.values_list("region_name", flat=True).distinct()
        ],
        label="",
        empty_label="-- region --",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    status = ChoiceFilter(
        field_name="status",
        choices=Mission.STATUS_CHOICES,
        label="",
        empty_label="-- status --",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    patch_test = BooleanFilter(
        field_name="patch_test",
        label="Patch Test",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
    )
    mgds_compilation = ChoiceFilter(
        field_name="mgds_compilation",
        choices=[
            (m, m)
            for m in Mission.objects.values_list(
                "mgds_compilation", flat=True
            ).distinct()
        ],
        label="",
        empty_label="-- MGDS_compilation --",
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    expedition__name = CharFilter(
        field_name="expedition__name",
        lookup_expr="icontains",
        label="",
        widget=TextInput(attrs={"placeholder": "Expedition name contains..."}),
    )

    class Meta:
        model = Mission
        fields = [
            "name",
            "region_name",
            "status",
            "patch_test",
            "mgds_compilation",
            "expedition__name",
        ]


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
