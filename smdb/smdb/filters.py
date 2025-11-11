from django import forms
from django_filters import (
    FilterSet,
    CharFilter,
    ChoiceFilter,
    ModelMultipleChoiceFilter,
)
from django.db.utils import ProgrammingError
import logging
from smdb.models import Mission, Expedition, Compilation, Quality_Category

from django.forms.widgets import TextInput

logger = logging.getLogger(__name__)


class MissionFilter(FilterSet):
    name = CharFilter(
        field_name="name",
        lookup_expr="icontains",
        label="",
        widget=TextInput(attrs={"placeholder": "Name contains..."}),
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate region_name choices at form instantiation time
        try:
            if "region_name" in self.filters and "region_name" in self.form.fields:
                # Get all distinct region_name values, excluding null and empty strings
                # Use list() to force queryset evaluation and filter out None/empty/whitespace values
                # First, get total count for debugging
                total_missions = Mission.objects.count()
                regions_queryset = Mission.objects.values_list("region_name", flat=True).distinct().exclude(region_name__isnull=True).exclude(region_name="")
                regions = list(regions_queryset)
                # Filter out None, empty strings, and whitespace-only strings, then create choices
                region_choices = [(r, r) for r in regions if r and r.strip()]
                # Sort choices alphabetically for better UX
                region_choices.sort(key=lambda x: x[0])
                # Debug logging - use info level so it's visible
                logger.info(f"Total missions in DB: {total_missions}, Found {len(regions)} raw region_name values, {len(region_choices)} valid region_name choices: {[r[0] for r in region_choices[:10]]}")
                # Update both the form field's choices and the widget's choices
                if region_choices:
                    choices_list = [("", "- region -")] + region_choices
                    # Set on the form field
                    self.form.fields["region_name"].choices = choices_list
                    # Also update the widget's choices - some widgets need this set explicitly
                    widget = self.form.fields["region_name"].widget
                    widget.choices = choices_list
                    # For Select widgets, also try setting the widget's _choices attribute (internal Django attribute)
                    if hasattr(widget, '_choices'):
                        widget._choices = choices_list
                    # Force widget to update by accessing its choices property
                    _ = widget.choices  # This forces Django to process the choices
                    logger.info(f"Set {len(choices_list)} choices on region_name widget (including empty option)")
                else:
                    # Even if no choices, ensure empty option is there
                    empty_choices = [("", "- region -")]
                    self.form.fields["region_name"].choices = empty_choices
                    if hasattr(self.form.fields["region_name"].widget, 'choices'):
                        self.form.fields["region_name"].widget.choices = empty_choices
        except (ProgrammingError, KeyError, AttributeError) as e:
            # Likely error on initial migrate or if region_name filter doesn't exist
            # Log the error for debugging
            logger.warning(f"Error populating region_name choices: {e}")
            pass
        
        # Dynamically populate mgds_compilation choices at form instantiation time
        try:
            if "mgds_compilation" in self.filters and "mgds_compilation" in self.form.fields:
                # Get all distinct mgds_compilation values, excluding null and empty strings
                # Use list() to force queryset evaluation and filter out None/empty/whitespace values
                # First, get total count for debugging
                total_missions = Mission.objects.count()
                mgds_comps_queryset = Mission.objects.values_list("mgds_compilation", flat=True).distinct().exclude(mgds_compilation__isnull=True).exclude(mgds_compilation="")
                mgds_comps = list(mgds_comps_queryset)
                # Filter out None, empty strings, and whitespace-only strings, then create choices
                mgds_choices = [(m, m) for m in mgds_comps if m and m.strip()]
                # Sort choices alphabetically for better UX
                mgds_choices.sort(key=lambda x: x[0])
                # Debug logging - use info level so it's visible
                logger.info(f"Total missions in DB: {total_missions}, Found {len(mgds_comps)} raw mgds_compilation values, {len(mgds_choices)} valid mgds_compilation choices: {[m[0] for m in mgds_choices[:10]]}")
                # Update both the form field's choices and the widget's choices
                if mgds_choices:
                    choices_list = [("", "- MGDS_compilation -")] + mgds_choices
                    # Set on the form field
                    self.form.fields["mgds_compilation"].choices = choices_list
                    # Also update the widget's choices - some widgets need this set explicitly
                    widget = self.form.fields["mgds_compilation"].widget
                    widget.choices = choices_list
                    # For Select widgets, also try setting the widget's _choices attribute (internal Django attribute)
                    if hasattr(widget, '_choices'):
                        widget._choices = choices_list
                    # Force widget to update by accessing its choices property
                    _ = widget.choices  # This forces Django to process the choices
                    logger.info(f"Set {len(choices_list)} choices on mgds_compilation widget (including empty option)")
                else:
                    # Even if no choices, ensure empty option is there
                    empty_choices = [("", "- MGDS_compilation -")]
                    self.form.fields["mgds_compilation"].choices = empty_choices
                    if hasattr(self.form.fields["mgds_compilation"].widget, 'choices'):
                        self.form.fields["mgds_compilation"].widget.choices = empty_choices
        except (ProgrammingError, KeyError, AttributeError) as e:
            # Likely error on initial migrate or if mgds_compilation filter doesn't exist
            # Log the error for debugging
            logger.warning(f"Error populating mgds_compilation choices: {e}")
            pass
    
    try:
        region_name = ChoiceFilter(
            field_name="region_name",
            choices=[],  # Will be populated dynamically in __init__
            label="",
            empty_label="- region -",
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
            choices=[],  # Will be populated dynamically in __init__
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
