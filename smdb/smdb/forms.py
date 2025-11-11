from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Row, Column, Reset


class MissionFilterFormHelper(FormHelper):
    form_method = "GET"
    layout = Layout(
        Row(
            Column("name", css_class="form-group col-md mb-0"),
            Column("region_name", css_class="form-group col-md mb-0"),
            Column("quality_categories", css_class="form-group col-md mb-0"),
            Column("patch_test", css_class="form-group col-md mb-0"),
            Column("repeat_survey", css_class="form-group col-md mb-0"),
            Column("mgds_compilation", css_class="form-group col-md mb-0"),
            Column("expedition__name", css_class="form-group col-md mb-0"),
            Column(Submit("submit", "Filter", css_id="missionFilterSubmit", css_class="col-md mb-0 btn-primary")),
            Column(
                Reset(
                    "clear",
                    "Clear",
                    css_id="missionFilterCancel",
                    css_class="col-md mb-0 btn-secondary",
                    onclick='window.location.href="{}"'.format('/missions'),
                    type="button",
                )
            ),
        css_id="missionRow",
        css_class="missionRow"),
    )


class ExpeditionFilterFormHelper(FormHelper):
    form_method = "GET"
    layout = Layout(
        Row(
            Column("name", css_id="expeditionFilterName", css_class="form-group col-md-12 mb-0"),
        ),
        Row(
            Column(Submit("submit", "Filter", css_id="expeditionFilterSubmit", css_class="col-md mb-0 btn-primary")),
            Column(
                Reset(
                    "clear",
                    "Clear",
                    css_id="expeditionFilterCancel",
                    css_class="col-md mb-0 btn-secondary",
                    onclick='window.location.href="{}"'.format('/expeditions'),
                    type="button",
                )
            ),
        ),
    )


class CompilationFilterFormHelper(FormHelper):
    form_method = "GET"
    layout = Layout(
        Row(
            Column("name", css_id="compilationFilterName", css_class="form-group col-md-12 mb-0"),
        ),
        Row(
            Column(Submit("submit", "Filter", css_id="compilationFilterSubmit", css_class="col-md mb-0 btn-primary")),
            Column(
                Reset(
                    "clear",
                    "Clear",
                    css_id="compilationFilterCancel",
                    css_class="col-md mb-0 btn-secondary",
                    onclick='window.location.href="{}"'.format('/compilations'),
                    type="button",
                )
            ),
        ),
    )
