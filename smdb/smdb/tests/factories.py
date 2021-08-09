from factory import Faker, post_generation
from factory.django import DjangoModelFactory
from smdb.models import Mission, MissionType, Person
from typing import Any, Sequence

from django.contrib.auth import get_user_model


class MissionTypeFactory(DjangoModelFactory):
    missiontype_name = Faker("user_name")

    class Meta:
        model = MissionType
        django_get_or_create = ["missiontype_name"]


class PersonFactory(DjangoModelFactory):
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    institution_name = Faker("company")

    class Meta:
        model = Person


""" Waiting for serialization
class MissionFactory(DjangoModelFactory):

    mission_name = Faker("mission_name")
    name = Faker("name")

    class Meta:
        model = Mission
        django_get_or_create = ["mission_name"]
"""
