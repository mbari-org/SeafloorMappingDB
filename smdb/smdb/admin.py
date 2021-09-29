from django.contrib.gis.admin import GeoModelAdmin, register

from smdb.models import (
    Citation,
    Compilation,
    DataArchival,
    Expedition,
    Mission,
    Missiontype,
    Person,
    Platform,
    Platformtype,
    Sensor,
    Sensortype,
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
    ordering = [
        "name",
    ]
    search_fields = [
        "name",
        "mission__name",
        "expd_db_id",
    ]


@register(Mission)
class MissionAdmin(GeoModelAdmin):
    ordering = [
        "name",
    ]
    search_fields = [
        "name",
        "note__text",
    ]


@register(Missiontype)
class MissiontypeAdmin(GeoModelAdmin):
    pass


@register(Person)
class PersonAdmin(GeoModelAdmin):
    list_display = ("last_name", "first_name", "institution_name")


@register(Platform)
class PlatformAdmin(GeoModelAdmin):
    pass


@register(Platformtype)
class PlatformtypeAdmin(GeoModelAdmin):
    pass


@register(Sensor)
class SensorAdmin(GeoModelAdmin):
    pass


@register(Sensortype)
class SensortypeAdmin(GeoModelAdmin):
    pass

