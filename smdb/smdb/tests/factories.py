from factory import Faker, post_generation
from factory.django import DjangoModelFactory
from smdb.models import Mission, Missiontype, Person, Platformtype
from typing import Any, Sequence

from django.contrib.auth import get_user_model


class MissiontypeFactory(DjangoModelFactory):
    name = Faker("user_name")

    class Meta:
        model = Missiontype
        django_get_or_create = ["name"]


class PersonFactory(DjangoModelFactory):
    first_name = Faker("first_name")
    last_name = Faker("last_name")
    institution_name = Faker("company")

    class Meta:
        model = Person


class PlatformtypeFactory(DjangoModelFactory):
    name = Faker("user_name")

    class Meta:
        model = Platformtype


""" Waiting for serialization
class MissionFactory(DjangoModelFactory):

    name = Faker("name")
    name = Faker("name")

    class Meta:
        model = Mission
        django_get_or_create = ["name"]
"""
