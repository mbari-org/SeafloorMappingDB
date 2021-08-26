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
# ===== MissionType =====
class CreateMissionType(graphene.Mutation):
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
    class Arguments:
        missiontype_name = graphene.String()

    missiontype = graphene.Field(MissionTypeType)

    def mutate(self, info, missiontype_name):
        missiontype = MissionType.objects.get(
            missiontype_name=missiontype_name,
        )

        missiontype.delete()
        return DeleteMissionType(missiontype=missiontype)


# ===== Person =====
class CreatePerson(graphene.Mutation):
    class Arguments:
        first_name = graphene.String()
        last_name = graphene.String()
        institution_name = graphene.String()

    person = graphene.Field(PersonType)

    def mutate(self, info, first_name, last_name, institution_name):
        person = Person.objects.create(
            first_name=first_name,
            last_name=last_name,
            institution_name=institution_name,
        )

        person.save()
        return CreatePerson(person=person)


class UpdatePerson(graphene.Mutation):
    class Arguments:
        uuid = graphene.String(required=True)
        first_name = graphene.String()
        last_name = graphene.String()
        institution_name = graphene.String()

    person = graphene.Field(PersonType)

    def mutate(self, info, uuid, first_name, last_name, institution_name):
        person = Person.objects.get(uuid=uuid)
        person.first_name = first_name
        person.last_name = last_name
        person.institution_name = institution_name
        person.save()
        return UpdatePerson(person=person)


class DeletePerson(graphene.Mutation):
    class Arguments:
        uuid = graphene.String()

    person = graphene.Field(PersonType)

    def mutate(self, info, uuid):
        person = Person.objects.get(uuid=uuid)

        person.delete()
        return DeletePerson(person=person)


class Mutation(graphene.ObjectType):
    create_missiontype = CreateMissionType.Field()
    update_missiontype = UpdateMissionType.Field()
    delete_missiontype = DeleteMissionType.Field()

    create_person = CreatePerson.Field()
    update_person = UpdatePerson.Field()
    delete_person = DeletePerson.Field()


schema = graphene.Schema(query=Query, mutation=Mutation, auto_camelcase=False)

schema = graphene.Schema(query=Query, mutation=Mutation, auto_camelcase=False)
