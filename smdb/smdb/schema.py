import graphene
from graphene_django import DjangoObjectType

from smdb.models import MissionType, Person, PlatformType


class MissionTypeType(DjangoObjectType):
    class Meta:
        model = MissionType
        fields = ("uuid", "missiontype_name")


class PersonType(DjangoObjectType):
    class Meta:
        model = Person
        fields = ("uuid", "first_name", "last_name", "institution_name")


class PlatformTypeType(DjangoObjectType):
    class Meta:
        model = PlatformType
        fields = (
            "uuid",
            "platformtype_name",
        )


class Query(graphene.ObjectType):
    all_missiontypes = graphene.List(MissionTypeType)
    all_persons = graphene.List(PersonType)
    all_platformtypes = graphene.List(PlatformTypeType)
    missiontype_by_name = graphene.Field(
        MissionTypeType, name=graphene.String(required=True)
    )

    def resolve_all_missiontypes(root, info):
        return MissionType.objects.all()

    def resolve_all_persons(root, info):
        return Person.objects.all()

    def resolve_all_platformtypes(root, info):
        return PlatformType.objects.all()

    def resolve_missiontype_by_name(root, info, name):
        try:
            return MissionType.objects.get(missiontype_name=name)
        except MissionType.DoesNotExist:
            return None


schema = graphene.Schema(query=Query)
