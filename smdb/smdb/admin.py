from django.contrib.gis.admin import GeoModelAdmin, register

from smdb.models import (Citation, CitationMission, Compilation, DataArchival,
                         DataArchivalMission, Expedition, Mission, MissionType,
                         Person, Platform, PlatformType, Sensor, SensorMission,
                         SensorType,)

@register(Citation)
class CitationAdmin(GeoModelAdmin):
    pass


@register(CitationMission)
class CitationMissionAdmin(GeoModelAdmin):
    pass


@register(Compilation)
class CompilationAdmin(GeoModelAdmin):
    pass


@register(DataArchival)
class DataArchivalAdmin(GeoModelAdmin):
    pass


@register(DataArchivalMission)
class DataArchivalMissionAdmin(GeoModelAdmin):
    pass


@register(Expedition)
class ExpeditionAdmin(GeoModelAdmin):
    pass


@register(Mission)
class MissionAdmin(GeoModelAdmin):
    pass


@register(MissionType)
class MissionTypeAdmin(GeoModelAdmin):
    pass


@register(Person)
class PersonAdmin(GeoModelAdmin):
    list_display = ('last_name', 'first_name', 'institution_name')
    pass


@register(Platform)
class PlatformAdmin(GeoModelAdmin):
    pass


@register(PlatformType)
class PlatformTypeAdmin(GeoModelAdmin):
    pass


@register(Sensor)
class SensorAdmin(GeoModelAdmin):
    pass


@register(SensorMission)
class SensorMissionAdmin(GeoModelAdmin):
    pass


@register(SensorType)
class SensorTypeAdmin(GeoModelAdmin):
    pass
