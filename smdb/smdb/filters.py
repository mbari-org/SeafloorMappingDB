from django import forms
from django.http import QueryDict
from django_filters import (
    FilterSet,
    CharFilter,
    ChoiceFilter,
    ModelMultipleChoiceFilter,
    MultipleChoiceFilter,
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
    vehicle_name = MultipleChoiceFilter(
        field_name="vehicle_name",
        choices=[
            # Vehicle options
            ("MAUV1", "MAUV1"),
            ("LASS", "LASS"),
            ("MAUV2", "MAUV2"),
            ("Sentry", "Sentry"),
            ("ABE", "ABE"),
            # Platform options
            ("R/V David Packard", "R/V David Packard"),
            ("Paragon", "R/V Paragon"),
            ("Iceberg", "Iceberg"),
            ("", "None"),  # Use empty string for None/null values
        ],
        label="",
        widget=forms.SelectMultiple(
            attrs={"class": "form-control", "size": 2, "style": "font-size: x-small;"}
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
            "vehicle_name",
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
        
        Supports:
        - Single word searches: "Northern" finds missions with "Northern" anywhere in name or expedition name
        - Multiple word searches: "Northern Mapping" finds missions containing BOTH "Northern" AND "Mapping"
        - Partial word searches: "Map" finds "Mapping", "Map", "Mapped", etc.
        - Case-insensitive searches
        - Searches across both mission names and expedition names (OR logic for fields)
        """
        # Get the search values for name and expedition__name
        name_value = self.data.get('name', '').strip()
        expedition_name_value = self.data.get('expedition__name', '').strip()
        
        # Handle vehicle_name filter separately to handle None values
        vehicle_name_values = self.data.getlist('vehicle_name', [])
        
        # Create a copy of data without name and vehicle_name fields to avoid double filtering
        filtered_data = QueryDict(mutable=True)
        for key, value_list in self.data.lists():
            if key not in ['name', 'expedition__name', 'vehicle_name']:
                filtered_data.setlist(key, value_list)
        
        # Temporarily replace data to exclude name and vehicle_name fields from base filtering
        original_data = self.data
        self.data = filtered_data
        
        # Get the base filtered queryset with AND logic for other fields
        qs = super().filter_queryset(queryset)
        
        # Restore original data
        self.data = original_data
        
        # Apply vehicle_name filter manually to handle None/empty values
        if vehicle_name_values:
            vehicle_q = Q()
            for vehicle_value in vehicle_name_values:
                # Handle None/empty values - empty string represents None/null
                if vehicle_value == '' or vehicle_value is None:
                    # Handle None/empty values
                    vehicle_q |= Q(vehicle_name__isnull=True) | Q(vehicle_name='')
                else:
                    vehicle_q |= Q(vehicle_name=vehicle_value)
            qs = qs.filter(vehicle_q)
        
        # Apply OR logic for text search fields
        if name_value or expedition_name_value:
            # Build OR conditions for text search
            text_search_q = Q()
            
            # Helper function to build search query for a search term
            def build_search_query(search_term):
                """
                Build a Q object that searches for search_term in both mission name and expedition name.
                If search_term contains multiple words (separated by spaces), each word must be found
                (AND logic for words, OR logic for fields).
                """
                if not search_term:
                    return Q()
                
                # Split by whitespace to handle multiple words
                words = search_term.split()
                
                if len(words) == 1:
                    # Single word: search in both fields (OR logic)
                    single_word = words[0]
                    return Q(name__icontains=single_word) | Q(expedition__name__icontains=single_word)
                else:
                    # Multiple words: each word must be found somewhere (AND logic for words)
                    # But can be in either mission name OR expedition name (OR logic for fields)
                    multi_word_q = Q()
                    for word in words:
                        # Each word must appear in at least one of the fields
                        word_q = Q(name__icontains=word) | Q(expedition__name__icontains=word)
                        if multi_word_q:
                            # AND logic: combine with existing conditions
                            multi_word_q &= word_q
                        else:
                            multi_word_q = word_q
                    return multi_word_q
            
            if name_value:
                # Search in both mission name and expedition name when name is provided
                name_query = build_search_query(name_value)
                if name_query:
                    text_search_q |= name_query
            
            if expedition_name_value:
                # Search in both mission name and expedition name when expedition__name is provided
                expedition_query = build_search_query(expedition_name_value)
                if expedition_query:
                    text_search_q |= expedition_query
            
            # Apply the text search filter if we have any conditions
            if text_search_q:
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
