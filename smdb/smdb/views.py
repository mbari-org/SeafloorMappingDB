import json
import logging

from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.core.serializers import serialize
from django.db import connection

from smdb.models import Mission


class MissionOverView(TemplateView):
    logger = logging.getLogger(__name__)
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):

        """Return the view context data."""
        context = super().get_context_data(**kwargs)
        missions = Mission.objects.all()
        ##missions = Mission.objects.filter(mission_name__contains="lidar")
        self.logger.info(f"Serializing {missions.count()} missions to geojson...")
        context["missions"] = json.loads(serialize("geojson", missions, fields=('grid_bounds', 'mission_name')))
        self.logger.info(f"# of Queries: {len(connection.queries)}")
        self.logger.info((f"Size of context['missions']: {len(str(context['missions']))}"))
        self.logger.debug(f"context['missions'] = { json.dumps(context['missions'], indent=4, sort_keys=True)}")

        return context