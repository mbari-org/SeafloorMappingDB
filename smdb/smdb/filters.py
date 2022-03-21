from django_filters import FilterSet, CharFilter, BooleanFilter
from smdb.models import Mission, Expedition, Compilation


class MissionFilter(FilterSet):
    name = CharFilter(field_name="name", lookup_expr="icontains")
    expedition__name = CharFilter(
        field_name="expedition__name", lookup_expr="icontains"
    )

    class Meta:
        model = Mission
        fields = ["name", "expedition__name"]


class ExpeditionFilter(FilterSet):
    name = CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Expedition
        fields = [
            "name",
        ]


class CompilationFilter(FilterSet):
    name = CharFilter(field_name="name", lookup_expr="icontains")
    has_missions = BooleanFilter(
        field_name="missions", lookup_expr="isnull", exclude=True, label="Has Missions"
    )

    class Meta:
        model = Compilation
        fields = [
            "name",
        ]
