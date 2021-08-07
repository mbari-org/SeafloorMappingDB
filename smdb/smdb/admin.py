from django.contrib.gis.admin import GeoModelAdmin, register

from smdb.models import (
    Citation,
    Compilation,
    DataArchival,
    Expedition,
    Mission,
    MissionType,
    Note,
    Person,
    Platform,
    PlatformType,
    Sensor,
    SensorType,
)


@register(Citation)
class CitationAdmin(GeoModelAdmin):
    pass


@register(Compilation)
class CompilationAdmin(GeoModelAdmin):
    pass


@register(DataArchival)
class DataArchivalAdmin(GeoModelAdmin):
    pass


@register(Expedition)
class ExpeditionAdmin(GeoModelAdmin):
    pass


@register(Mission)
class MissionAdmin(GeoModelAdmin):
    search_fields = [
        "mission_name",
    ]


@register(MissionType)
class MissionTypeAdmin(GeoModelAdmin):
    pass


@register(Person)
class PersonAdmin(GeoModelAdmin):
    list_display = ("last_name", "first_name", "institution_name")


@register(Platform)
class PlatformAdmin(GeoModelAdmin):
    pass


@register(PlatformType)
class PlatformTypeAdmin(GeoModelAdmin):
    pass


@register(Sensor)
class SensorAdmin(GeoModelAdmin):
    pass


@register(SensorType)
class SensorTypeAdmin(GeoModelAdmin):
    pass


@register(Note)
class NoteAdmin(GeoModelAdmin):
    search_fields = ["text"]
