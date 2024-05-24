from django import forms
from django_filters import (
    FilterSet,
    CharFilter,
    BooleanFilter,
    ChoiceFilter,
    ModelMultipleChoiceFilter,
)
from smdb.models import Mission, Expedition, Compilation, Quality_Category

from django.forms.widgets import TextInput


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
        empty_label="- region -",
        widget=forms.Select(
            attrs={"class": "form-control", "style": "font-weight: 300;"}
        ),
    )
    quality_categories = ModelMultipleChoiceFilter(
        field_name="quality_categories__name",
        queryset=Quality_Category.objects.all(),
        to_field_name="name",
        label="",
        widget=forms.SelectMultiple(
            attrs={"class": "form-control", "size": 2, "style": "font-size: x-small;"}
        ),
    )
    patch_test = ChoiceFilter(
        field_name="patch_test",
        choices=[(None, "-"), (True, "Yes"), (False, "No")],
        label="",
        empty_label="- Patch Test -",
        widget=forms.Select(
            attrs={"class": "form-control", "style": "font-weight: 300;"}
        ),
    )
    repeat_survey = ChoiceFilter(
        field_name="repeat_survey",
        choices=[(None, "-"), (True, "Yes"), (False, "No")],
        label="",
        empty_label="- Repeat Survey -",
        widget=forms.Select(
            attrs={"class": "form-control", "style": "font-weight: 300;"}
        ),
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
        empty_label="- MGDS_compilation -",
        widget=forms.Select(
            attrs={"class": "form-control", "style": "font-weight: 300;"}
        ),
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
            "quality_categories",
            "patch_test",
            "repeat_survey",
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
