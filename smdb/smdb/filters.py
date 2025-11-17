from django import forms
from django.http import QueryDict
from django_filters import (
    FilterSet,
    CharFilter,
    ChoiceFilter,
    ModelMultipleChoiceFilter,
)
from django.db.utils import ProgrammingError
from django.db.models import Q
from smdb.models import Mission, Expedition, Compilation, Quality_Category

from django.forms.widgets import TextInput


class MissionFilter(FilterSet):
    name = CharFilter(
        field_name="name",
        lookup_expr="icontains",
        label="",
        widget=TextInput(attrs={"placeholder": "Survey name contains..."}),
    )
    try:
        region_name = ChoiceFilter(
            field_name="region_name",
            choices=[
                (m, m)
                for m in Mission.objects.values_list("region_name", flat=True).distinct()
            ],
            label="",
            empty_label="- Location -",
            widget=forms.Select(
                attrs={
                    "class": "form-control",
                    "style": "font-weight: 300; font-size: smaller;",
                }
            ),
        )
    except ProgrammingError as e:
        # Likely error on initial migrate done with start command creating the smdb database
        pass
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
        choices=[(None, "-"), (True, "✔")],
        label="",
        empty_label="- Patch Test -",
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "style": "font-weight: 300; font-size: smaller;",
            }
        ),
    )
    repeat_survey = ChoiceFilter(
        field_name="repeat_survey",
        choices=[(None, "-"), (True, "✔")],
        label="",
        empty_label="- Repeat Survey -",
        widget=forms.Select(
            attrs={
                "class": "form-control",
                "style": "font-weight: 300; font-size: smaller;",
            }
        ),
    )
    try:
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
                attrs={
                    "class": "form-control",
                    "style": "font-weight: 300; font-size: smaller;",
                }
            ),
        )
    except ProgrammingError as e:
        # Likely error on initial migrate done with start command creating the smdb database
        pass
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
    
    def filter_queryset(self, queryset):
        """
        Override to use OR logic for name and expedition__name text search fields.
        This allows searching for partial words like "Northern", "Auv", "Ops" 
        in either field to find matches in both mission names and expedition names.
        """
        # Get the search values for name and expedition__name
        name_value = self.data.get('name', '').strip()
        expedition_name_value = self.data.get('expedition__name', '').strip()
        
        # Create a copy of data without name fields to avoid double filtering
        filtered_data = QueryDict(mutable=True)
        for key, value_list in self.data.lists():
            if key not in ['name', 'expedition__name']:
                filtered_data.setlist(key, value_list)
        
        # Temporarily replace data to exclude name fields from base filtering
        original_data = self.data
        self.data = filtered_data
        
        # Get the base filtered queryset with AND logic for other fields
        qs = super().filter_queryset(queryset)
        
        # Restore original data
        self.data = original_data
        
        # Apply OR logic for text search fields
        if name_value or expedition_name_value:
            # Build OR conditions for text search
            text_search_q = Q()
            
            if name_value:
                # Search in both mission name and expedition name when name is provided
                text_search_q |= Q(name__icontains=name_value) | Q(expedition__name__icontains=name_value)
            
            if expedition_name_value:
                # Search in both mission name and expedition name when expedition__name is provided
                text_search_q |= Q(name__icontains=expedition_name_value) | Q(expedition__name__icontains=expedition_name_value)
            
            # Apply the text search filter
            qs = qs.filter(text_search_q)
        
        return qs


class ExpeditionFilter(FilterSet):
    name = CharFilter(
        field_name="name",
        lookup_expr="icontains",
        label="",
        widget=TextInput(attrs={"placeholder": "Name contains..."}),
    )

    class Meta:
        model = Expedition
        fields = [
            "name",
        ]


class CompilationFilter(FilterSet):
    name = CharFilter(
        field_name="name",
        lookup_expr="icontains",
        label="",
        widget=TextInput(attrs={"placeholder": "Name contains..."}),
    )

    class Meta:
        model = Compilation
        fields = [
            "name",
        ]
