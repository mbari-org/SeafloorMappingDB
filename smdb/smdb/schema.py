import uuid as uuid_lib

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


# https://medium.com/analytics-vidhya/graphql-with-django-simple-yet-powerful-crud-part-2-bacce3668e35
class CreateMissionType(graphene.Mutation):
    """Example creation query:
    mutation {
        create_missiontype(missiontype_name: "graphQL-Test") {
            missiontype {
            missiontype_name
            }
        }
    }
    """

    class Arguments:
        missiontype_name = graphene.String()

    missiontype = graphene.Field(MissionTypeType)

    def mutate(self, info, missiontype_name):
        missiontype = MissionType.objects.create(
            missiontype_name=missiontype_name,
        )

        missiontype.save()
        return CreateMissionType(missiontype=missiontype)


class UpdateMissionType(graphene.Mutation):
    """Example update query:
    mutation {
        update_missiontype(missiontype_name: "graphQL-Test", new_missiontype_name: "updated-graphQL-Test") {
            missiontype {
            missiontype_name
            }
        }
    }
    """

    class Arguments:
        missiontype_name = graphene.String(required=True)
        new_missiontype_name = graphene.String(required=True)

    missiontype = graphene.Field(MissionTypeType)

    def mutate(self, info, missiontype_name, new_missiontype_name):
        missiontype = MissionType.objects.get(
            missiontype_name=missiontype_name,
        )
        missiontype.missiontype_name = new_missiontype_name
        missiontype.save()
        return UpdateMissionType(missiontype=missiontype)


class DeleteMissionType(graphene.Mutation):
    """Example deletion query:
    mutation {
        delete_missiontype(missiontype_name: "updated-graphQL-Test") {
            missiontype {
            missiontype_name
            }
        }
    }
    """

    class Arguments:
        missiontype_name = graphene.String()

    missiontype = graphene.Field(MissionTypeType)

    def mutate(self, info, missiontype_name):
        missiontype = MissionType.objects.get(
            missiontype_name=missiontype_name,
        )

        missiontype.delete()
        return DeleteMissionType(missiontype=missiontype)


class Mutation(graphene.ObjectType):
    create_missiontype = CreateMissionType.Field()
    update_missiontype = UpdateMissionType.Field()
    delete_missiontype = DeleteMissionType.Field()


schema = graphene.Schema(query=Query, mutation=Mutation, auto_camelcase=False)
