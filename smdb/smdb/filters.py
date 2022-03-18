from django_filters import FilterSet, CharFilter
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

    class Meta:
        model = Compilation
        fields = [
            "name",
        ]
