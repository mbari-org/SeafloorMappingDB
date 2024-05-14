from tabnanny import verbose
from django_tables2 import Table, Column, ManyToManyColumn
from django.utils.html import mark_safe

from smdb.models import Compilation, Expedition, Mission, MBARI_DIR


# https://stackoverflow.com/a/19947056/1281657
class DivWrappedColumn(Column):
    def __init__(self, classname=None, *args, **kwargs):
        self.classname = classname
        super(DivWrappedColumn, self).__init__(*args, **kwargs)

    def render(self, value):
        value = value.replace(MBARI_DIR, "")
        return mark_safe("<div class='" + self.classname + "' >" + value + "</div>")


class MissionTable(Table):
    name = Column(linkify=True)
    expedition = Column(linkify=True)
    compilation_set = ManyToManyColumn(linkify_item=True, verbose_name="Compilations")

    class Meta:
        model = Mission
        fields = (
            "name",
            "track_length",
            "start_depth",
        )
        sequence = (
            "name",
            "track_length",
            "start_depth",
            "expedition",
            "compilation_set",
        )


class ExpeditionTable(Table):
    name = Column(linkify=True)
    mission_set = ManyToManyColumn(
        linkify_item=True,
        verbose_name="Missions",
    )

    class Meta:
        model = Expedition
        fields = ("name", "expd_db_id")
        sequence = ("name", "expd_db_id", "mission_set")


class CompilationTable(Table):
    name = DivWrappedColumn(linkify=True, classname="")
    thumbnail_filename = DivWrappedColumn(classname="")
    missions = ManyToManyColumn(linkify_item=True, verbose_name="Missions")

    class Meta:
        model = Compilation
        fields = ("name", "creation_date")
        sequence = ("name", "thumbnail_filename", "creation_date", "missions")
