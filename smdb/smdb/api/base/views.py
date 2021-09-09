from django.contrib.auth import get_user_model
from rest_framework import status, permissions
from rest_framework.decorators import action
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ViewSet
from smdb.models import MissionType, Person, PlatformType
from .serializers import MissionTypeSerializer, PersonSerializer, PlatformTypeSerializer


# Modeled after UserViewSet
class MissionTypeViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = MissionTypeSerializer
    queryset = MissionType.objects.all()
    lookup_field = "missiontype_name"


class PersonViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = PersonSerializer
    queryset = Person.objects.all()
    lookup_field = "uuid"


class PlatformTypeViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = PlatformTypeSerializer
    queryset = PlatformType.objects.all()
    lookup_field = "name"


""" Waiting for better serializer implementaion
class MissionViewSet(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = MissionSerializer
    queryset = Mission.objects.all()
    lookup_field = "mission_name"
"""
