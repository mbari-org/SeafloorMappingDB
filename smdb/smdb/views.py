import json
import logging
from os.path import join

from django.conf import settings
from django.contrib.gis.geos import Polygon
from django.core.serializers import serialize
from django.db import connection
from django.db.models import Q, Min, Max
from django.views.generic import DetailView, ListView
from django.views.generic.base import TemplateView

from smdb.models import Expedition, Mission


class MissionOverView(TemplateView):
    logger = logging.getLogger(__name__)
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):

        """Return the view context data."""
        context = super().get_context_data(**kwargs)
        search_string = context["view"].request.GET.get("q")
        search_geom = None
        if context["view"].request.GET.get("bounds"):
            min_lon, min_lat, max_lon, max_lat = (
                context["view"].request.GET.get("bounds").split(",")
            )
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
        missions = Mission.objects.all()
        if search_string:
            self.logger.info("search_string = %s", search_string)
            missions = missions.filter(
                Q(name__icontains=search_string)
                | Q(notes_text__icontains=search_string)
            )
        if search_geom:
            missions = missions.filter(grid_bounds__contained=search_geom)

        self.logger.info(
            "Serializing %s missions to geojson...",
            missions.count(),
        )
        context["missions"] = json.loads(
            serialize(
                "geojson",
                missions,
                fields=(
                    "slug",
                    "nav_track",
                    "thumbnail_image",
                ),
                geometry_field="nav_track",
            )
        )
        self.logger.debug("# of Queries: %d", len(connection.queries))
        self.logger.debug(
            "Size of context['missions']: %d", len(str(context["missions"]))
        )
        self.logger.debug(
            "context['missions'] = %s",
            json.dumps(context["missions"], indent=4, sort_keys=True),
        )
        if search_string:
            context["search_string"] = "{:d} Missions containing '{:s}'".format(
                len(context["missions"]["features"]),
                search_string,
            )
        else:
            context[
                "search_string"
            ] = f"Displaying {len(context['missions']['features'])} Missions"
        time_bounds = missions.aggregate(Min("start_date"), Max("end_date"))
        context["start_esec"] = time_bounds["start_date__min"].timestamp()
        context["end_esec"] = time_bounds["end_date__max"].timestamp()
        return context


class MissionListView(ListView):
    model = Mission


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
        return context

    def get_object(self):
        obj = super().get_object()
        return obj


class ExpeditionListView(ListView):
    model = Expedition
    queryset = Expedition.objects.all()


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
