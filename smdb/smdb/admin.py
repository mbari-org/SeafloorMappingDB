from django import forms
from django.contrib.gis.admin import GeoModelAdmin, register
from django.contrib import admin

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


class CitationAdminForm(forms.ModelForm):
    """Allow full_reference to be empty in admin (model allows empty string from tally)."""

    class Meta:
        model = Citation
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["full_reference"].required = False
        if not self.fields["full_reference"].initial:
            self.fields["full_reference"].initial = ""


@register(Citation)
class CitationAdmin(admin.ModelAdmin):
    form = CitationAdminForm
    list_display = ("doi", "full_reference")
    list_filter = ()
    search_fields = ("doi", "full_reference")
    filter_horizontal = ("missions",)
    fields = ("doi", "full_reference", "missions")


@register(Compilation)
class CompilationAdmin(GeoModelAdmin):
    ordering = [
        "name",
    ]
    search_fields = [
        "name",
    ]
    fields = [
        "image_tag",
        "name",
        "slug",
        "creation_date",
        "cmd_filename",
        "grd_filename",
        "grid_bounds",
        "thumbnail_filename",
        "thumbnail_image",
    ]
    readonly_fields = ["image_tag"]
    prepopulated_fields = {"slug": ("name",)}


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
    prepopulated_fields = {"slug": ("name",)}


@register(Mission)
class MissionAdmin(GeoModelAdmin):
    ordering = [
        "name",
    ]
    search_fields = [
        "name",
        "notes_text",
    ]
    fields = [
        "image_tag",
        "expedition",
        "name",
        "slug",
        "start_date",
        "end_date",
        "track_length",
        "area",
        "nav_track",
        "start_depth",
        "comment",
        "quality_comment",
        "patch_test",
        "repeat_survey",
        "directory",
        "notes_filename",
        "notes_text",
        "region_name",
        "site_detail",
        "thumbnail_filename",
        "thumbnail_image",
        "kml_filename",
        "quality_categories",
        "citations",
    ]
    filter_horizontal = ("quality_categories", "citations")
    readonly_fields = ["image_tag", "area"]
    prepopulated_fields = {"slug": ("name",)}


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
