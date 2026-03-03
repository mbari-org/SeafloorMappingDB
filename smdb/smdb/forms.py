from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Row, Column, Reset


class MissionFilterFormHelper(FormHelper):
    form_method = "GET"
    layout = Layout(
        Row(
            Column("name", css_class="form-group col-md mb-0"),
            Column("region_name", css_class="form-group col-md mb-0"),
            Column("vehicle_name", css_class="form-group col-md mb-0"),
            Column("platformtype", css_class="form-group col-md mb-0"),
            Column("quality_categories", css_class="form-group col-md mb-0"),
            Column("patch_test", css_class="form-group col-md mb-0"),
            Column("repeat_survey", css_class="form-group col-md mb-0"),
            Column("mgds_compilation", css_class="form-group col-md mb-0"),
            Column("citation", css_class="form-group col-md mb-0"),
            Column("citation_search", css_class="form-group col-md mb-0"),
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
            Column("name", css_id="expeditionFilterName", css_class="form-group col-md-3 mb-0"),
            Div(
            Column(Submit("submit", "Filter", css_id="expeditionFilterSubmit", css_class="col-md mb-0 btn-primary")),
            ),
            Div(
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
        ),
    )


class CompilationFilterFormHelper(FormHelper):
    form_method = "GET"
    layout = Layout(
        Row(
            Column("name", css_id="compilationFilterName", css_class="form-group col-md-3 mb-0"),
            Div(
                Column(Submit("submit", "Filter", css_id="compilationFilterSubmit", css_class="col-md mb-0 btn-primary")),
            ),
            Div(
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
        ),
    )


class MissionFilterSidebarHelper(FormHelper):
    """
    Form helper for MissionFilter in the sidebar with vertical layout.
    Includes Filter and Clear buttons at the bottom.
    """
    form_method = "GET"
    layout = Layout(
        Div("name", css_class="mb-3"),
        Div("region_name", css_class="mb-3"),
        Div("vehicle_name", css_class="mb-3"),
        Div("platformtype", css_class="mb-3"),
        Div("quality_categories", css_class="mb-3"),
        Div("patch_test", css_class="mb-3"),
        Div("repeat_survey", css_class="mb-3"),
        Div("mgds_compilation", css_class="mb-3"),
        Div("citation", css_class="mb-3"),
        Div("citation_search", css_class="mb-3"),
        Div("expedition__name", css_class="mb-3"),
        # tmin and tmax are hidden fields, no need to include in layout
        # Buttons are created dynamically by JavaScript in map.js
        # Div(
        #     Submit("submit", "Filter", css_id="missionFilterSubmit", css_class="btn-primary"),
        #     Reset("clear", "Clear", css_id="missionFilterCancel", css_class="btn-secondary"),
        #     css_class="button-row mb-3",
        #     css_style="display: flex; gap: 0.5rem; margin-top: 0.5rem; width: 100%;"
        # ),
    )


class ExpeditionFilterSidebarHelper(FormHelper):
    """
    Form helper for ExpeditionFilter in the sidebar with vertical layout.
    Includes Filter and Clear buttons at the bottom.
    """
    form_method = "GET"
    layout = Layout(
        Div("name", css_class="mb-3"),
        # Buttons are created dynamically by JavaScript in map.js
        # Div(
        #     Submit("submit", "Filter", css_id="expeditionFilterSubmit", css_class="btn-primary"),
        #     Reset("clear", "Clear", css_id="expeditionFilterCancel", css_class="btn-secondary"),
        #     css_class="button-row mb-3",
        #     css_style="display: flex; gap: 0.5rem; margin-top: 0.5rem; width: 100%;"
        # ),
    )


class CompilationFilterSidebarHelper(FormHelper):
    """
    Form helper for CompilationFilter in the sidebar with vertical layout.
    Includes Filter and Clear buttons at the bottom.
    """
    form_method = "GET"
    layout = Layout(
        Div("name", css_class="mb-3"),
        # Buttons are created dynamically by JavaScript in map.js
        # Div(
        #     Submit("submit", "Filter", css_id="compilationFilterSubmit", css_class="btn-primary"),
        #     Reset("clear", "Clear", css_id="compilationFilterCancel", css_class="btn-secondary"),
        #     css_class="button-row mb-3",
        #     css_style="display: flex; gap: 0.5rem; margin-top: 0.5rem; width: 100%;"
        # ),
    )
