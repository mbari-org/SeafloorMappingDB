from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


class MissionFilterFormHelper(FormHelper):
    form_method = "GET"
    layout = Layout(
        Row(
            Column("name", css_class="form-group col-md-2 mb-0"),
            Column("expedition__name", css_class="form-group col-md-2 mb-0"),
            Column("status", css_class="form-group col-md-2 mb-0"),
            Column("patch_test", css_class="form-group col-md-1 mb-0"),
            Column(Submit("submit", "Filter", css_class="col-md-2 mb-0 btn-primary")),
        ),
    )
