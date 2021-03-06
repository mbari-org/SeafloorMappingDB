from rest_framework import serializers
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer,
    GeometrySerializerMethodField,
)
from smdb.models import Mission, Missiontype, Person, Platformtype


class MissiontypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Missiontype
        fields = ["name", "url"]
        extra_kwargs = {
            "url": {
                "view_name": "api:missiontype-detail",
                "lookup_field": "name",
            }
        }


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["uuid", "first_name", "last_name", "institution_name", "url"]
        extra_kwargs = {
            "url": {
                "view_name": "api:person-detail",
                "lookup_field": "uuid",
            }
        }


class PlatformtypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platformtype
        fields = ["name", "url"]
        extra_kwargs = {
            "url": {
                "view_name": "api:platformtype-detail",
                "lookup_field": "name",
            }
        }


""" Need to figure out how to serialize nested relationships and geometry types
class MissionSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Mission
        fields = ["name", "url"]
        grid_bounds = GeometrySerializerMethodField()
        extra_kwargs = {
            "url": {
                "view_name": "api:mission-detail",
                "lookup_field": "name",
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
