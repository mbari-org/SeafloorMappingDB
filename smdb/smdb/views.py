import json
import logging
import re
from os.path import join

from django.conf import settings
from django.contrib.gis.geos import Polygon
from django.db import connection
from django.db.models import Max, Min, Q
from django.views.generic import DetailView
from django.views.generic.base import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableView
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer,
    GeometrySerializerMethodField,
)

from smdb.filters import CompilationFilter, ExpeditionFilter, MissionFilter
from smdb.models import Compilation, Expedition, Mission, MBARI_DIR
from smdb.tables import CompilationTable, ExpeditionTable, MissionTable


class MissionSerializer(GeoFeatureModelSerializer):
    """Should probably be in smdb.api.base.serializers with a complete
    list fields, but here we have it just meeting our needs for MissionOverView()."""

    class Meta:
        model = Mission
        geo_field = "nav_track"
        fields = ("slug", "thumbnail_image", "start_date", "start_ems", "end_ems")
        nav_track = GeometrySerializerMethodField()


class MissionOverView(TemplateView):
    logger = logging.getLogger(__name__)
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):

        """Return the view context data."""
        context = super().get_context_data(**kwargs)
        search_string = context["view"].request.GET.get("q")
        search_geom = None
        if context["view"].request.GET.get("xmin"):
            min_lon = context["view"].request.GET.get("xmin")
            max_lon = context["view"].request.GET.get("xmax")
            min_lat = context["view"].request.GET.get("ymin")
            max_lat = context["view"].request.GET.get("ymax")
            search_geom = Polygon(
                (
                    (float(min_lon), float(min_lat)),
                    (float(min_lon), float(max_lat)),
                    (float(max_lon), float(max_lat)),
                    (float(max_lon), float(min_lat)),
                    (float(min_lon), float(min_lat)),
                ),
                srid=4326,
            )
        missions = Mission.objects.order_by("start_date").all()
        if search_string:
            self.logger.info("search_string = %s", search_string)
            missions = missions.filter(
                Q(name__icontains=search_string)
                | Q(notes_text__icontains=search_string)
            )
        if search_geom:
            missions = missions.filter(grid_bounds__contained=search_geom)
        if context["view"].request.GET.get("tmin"):
            min_date = context["view"].request.GET.get("tmin")
            max_date = context["view"].request.GET.get("tmax")
            missions = missions.filter(
                start_date__gte=min_date,
                end_date__lte=max_date,
            )

        self.logger.info(
            "Serializing %s missions to geojson...",
            missions.count(),
        )
        context["missions"] = MissionSerializer(missions, many=True).data
        self.logger.debug("# of Queries: %d", len(connection.queries))
        self.logger.debug(
            "Size of context['missions']: %d", len(str(context["missions"]))
        )
        self.logger.debug(
            "context['missions'] = %s",
            json.dumps(context["missions"], indent=4, sort_keys=True),
        )
        context["num_missions"] = len(context["missions"]["features"])
        if search_string:
            context["search_string"] = f"containing '{search_string}'"
        time_bounds = missions.aggregate(Min("start_date"), Max("end_date"))
        if time_bounds["start_date__min"]:
            context["start_ems"] = time_bounds["start_date__min"].timestamp() * 1000.0
        if time_bounds["end_date__max"]:
            context["end_ems"] = time_bounds["end_date__max"].timestamp() * 1000.0
        return context


class CompilationTableView(FilterView, SingleTableView):
    table_class = CompilationTable
    queryset = Compilation.objects.all()
    filterset_class = CompilationFilter


class ExpeditionTableView(FilterView, SingleTableView):
    table_class = ExpeditionTable
    queryset = Expedition.objects.all()
    filterset_class = ExpeditionFilter


class MissionTableView(FilterView, SingleTableView):
    table_class = MissionTable
    queryset = Mission.objects.all()
    filterset_class = MissionFilter


class MissionDetailView(DetailView):
    model = Mission
    queryset = Mission.objects.all()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        mission = super().get_object()
        try:
            context["thumbnail_url"] = mission.thumbnail_image.url
        except (AttributeError, ValueError):
            context["thumbnail_url"] = join(
                settings.STATIC_URL, "images", "No_ZTopoSlopeNav_image.jpg"
            )
        try:
            site_uri = self.request.build_absolute_uri("/")
            base_uri = re.match(r"(http[s]*:\/\/[^:\/]*)", site_uri).group(1)
            img_path = mission.thumbnail_filename.replace(MBARI_DIR, "")
            context["thumbnail_fullrez_url"] = join(
                base_uri, "SeafloorMapping", img_path
            )
        except (AttributeError, ValueError):
            # no thumbnail_filename - return something
            context["thumbnail_fullrez_url"] = base_uri
        return context

    def get_object(self):
        obj = super().get_object()
        return obj


class ExpeditionDetailView(DetailView):
    model = Expedition
    queryset = Expedition.objects.all()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        expedition = super().get_object()

        return context

    def get_object(self):
        obj = super().get_object()
        return obj


class CompilationDetailView(DetailView):
    model = Compilation
    queryset = Compilation.objects.all()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        compilation = super().get_object()
        try:
            context["thumbnail_url"] = compilation.thumbnail_image.url
        except (AttributeError, ValueError):
            context["thumbnail_url"] = join(
                settings.STATIC_URL, "images", "No_ZTopoSlopeNav_image.jpg"
            )
        try:
            site_uri = self.request.build_absolute_uri("/")
            base_uri = re.match(r"(http[s]*:\/\/[^:\/]*)", site_uri).group(1)
            img_path = compilation.thumbnail_filename.replace(MBARI_DIR, "")
            context["thumbnail_fullrez_url"] = join(
                base_uri, "SeafloorMapping", img_path
            )
        except (AttributeError, ValueError):
            # no thumbnail_filename - return something
            context["thumbnail_fullrez_url"] = base_uri
        return context

    def get_object(self):
        obj = super().get_object()
        return obj
