import json
import logging

from django.views.generic import ListView, DetailView
from django.views.generic.base import TemplateView
from django.core.serializers import serialize
from django.db import connection

from smdb.models import Mission, Note


class MissionOverView(TemplateView):
    logger = logging.getLogger(__name__)
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):

        """Return the view context data."""
        context = super().get_context_data(**kwargs)
        search_string = context["view"].request.GET.get("q")
        if search_string:
            missions = Mission.objects.filter(name__icontains=search_string)
        else:
            missions = Mission.objects.all()

        self.logger.info(
            "Serializing %s missions to geojson...",
            missions.count(),
        )
        context["missions"] = json.loads(
            serialize(
                "geojson",
                missions,
                fields=(
                    "pk",
                    "grid_bounds",
                    "name",
                    "thumbnail_image",
                ),
            )
        )
        self.logger.info("# of Queries: %s", len(connection.queries))
        self.logger.info(
            ("Size of context['missions']: %s", len(str(context["missions"])))
        )
        self.logger.debug(
            "context['missions'] = %s",
            json.dumps(context["missions"], indent=4, sort_keys=True),
        )

        if search_string:
            context[
                "search_string"
            ] = f"{len(context['missions']['features'])} Missions containing '{search_string}'"
        else:
            context[
                "search_string"
            ] = f"All {len(context['missions']['features'])} Missions"

        return context


class MissionListView(ListView):
    model = Mission


class MissionDetailView(DetailView):

    model = Mission
    queryset = Mission.objects.all()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        mission = super().get_object()
        context["note_text"] = Note.objects.get(mission=mission).text
        return context

    def get_object(self):
        obj = super().get_object()
        return obj
