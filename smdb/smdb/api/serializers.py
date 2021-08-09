from rest_framework import serializers
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer,
    GeometrySerializerMethodField,
)
from smdb.models import Mission, MissionType, Person


class MissionTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MissionType
        fields = ["missiontype_name", "url"]
        extra_kwargs = {
            "url": {
                "view_name": "api:missiontype-detail",
                "lookup_field": "missiontype_name",
            }
        }


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["first_name", "last_name", "institution_name", "url"]
        extra_kwargs = {
            "url": {
                "view_name": "api:person-detail",
                "lookup_field": "last_name",
            }
        }


""" Need to figure out how to serialize nested relationships and geometry types
class MissionSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Mission
        fields = ["mission_name", "url"]
        grid_bounds = GeometrySerializerMethodField()
        extra_kwargs = {
            "url": {
                "view_name": "api:mission-detail",
                "lookup_field": "mission_name",
            }
        }
        # https://github.com/openwisp/django-rest-framework-gis#bounding-box-auto_bbox-and-bbox_geo_field
        def get_grid_bounds(self, obj):
            grid_bounds = Polygon(
                (
                    (float(ds[X][0].data), float(ds[Y][0].data)),
                    (float(ds[X][0].data), float(ds[Y][-1].data)),
                    (float(ds[X][-1].data), float(ds[Y][-1].data)),
                    (float(ds[X][-1].data), float(ds[Y][0].data)),
                    (float(ds[X][0].data), float(ds[Y][0].data)),
                ),
                srid=4326,
            )

        return grid_bounds
"""
