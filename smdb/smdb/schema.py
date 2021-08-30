import graphene
from graphene_django import DjangoObjectType as DjangoObjectNode
from graphene_django.debug import DjangoDebug
from graphql import GraphQLError

from smdb.models import MissionType, Person, Platform, PlatformType, SensorType


class MissionTypeNode(DjangoObjectNode):
    class Meta:
        model = MissionType
        fields = ("uuid", "missiontype_name")


class PersonNode(DjangoObjectNode):
    class Meta:
        model = Person
        fields = ("uuid", "first_name", "last_name", "institution_name")


class PlatformTypeNode(DjangoObjectNode):
    class Meta:
        model = PlatformType
        fields = ("uuid", "platformtype_name")


class PlatformNode(DjangoObjectNode):
    class Meta:
        model = Platform
        fields = (
            "uuid",
            "platform_name",
            "operator_org_name",
            "platform_type",
        )


class SensorTypeNode(DjangoObjectNode):
    class Meta:
        model = SensorType
        fields = ("uuid", "sensortype_name")


class Query(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name="_debug")
    all_missiontypes = graphene.List(MissionTypeNode)
    all_persons = graphene.List(PersonNode)
    all_platformtypes = graphene.List(PlatformTypeNode)
    all_platforms = graphene.List(PlatformNode)
    all_sensortypes = graphene.List(SensorTypeNode)

    missiontype_by_name = graphene.Field(
        MissionTypeNode, name=graphene.String(required=True)
    )

    # Queries for all_ objects
    def resolve_all_missiontypes(root, info):
        return MissionType.objects.all()

    def resolve_all_persons(root, info):
        return Person.objects.all()

    def resolve_all_platformtypes(root, info):
        return PlatformType.objects.all()

    def resolve_all_platforms(root, info):
        return Platform.objects.all()

    def resolve_all_sensortypes(root, info):
        return SensorType.objects.all()

    # Specialized queries
    def resolve_missiontype_by_name(root, info, name):
        try:
            return MissionType.objects.get(missiontype_name=name)
        except MissionType.DoesNotExist:
            return None


# https://medium.com/analytics-vidhya/graphql-with-django-simple-yet-powerful-crud-part-2-bacce3668e35
# ===== MissionType =====
class MissionTypeInput(graphene.InputObjectType):
    missiontype_name = graphene.String(required=True)


class CreateMissionType(graphene.Mutation):
    class Arguments:
        missiontype_name = graphene.String()

    missiontype = graphene.Field(MissionTypeNode)

    def mutate(self, info, missiontype_name):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        missiontype = MissionType.objects.create(
            missiontype_name=missiontype_name,
        )
        missiontype.save()
        return CreateMissionType(missiontype=missiontype)


class UpdateMissionType(graphene.Mutation):
    class Arguments:
        missiontype_name = graphene.String(required=True)
        new_missiontype_name = graphene.String(required=True)

    missiontype = graphene.Field(MissionTypeNode)

    def mutate(self, info, missiontype_name, new_missiontype_name):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        missiontype = MissionType.objects.get(
            missiontype_name=missiontype_name,
        )
        missiontype.missiontype_name = new_missiontype_name
        missiontype.save()
        return UpdateMissionType(missiontype=missiontype)


class DeleteMissionType(graphene.Mutation):
    class Arguments:
        missiontype_name = graphene.String()

    missiontype = graphene.Field(MissionTypeNode)

    def mutate(self, info, missiontype_name):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        missiontype = MissionType.objects.get(
            missiontype_name=missiontype_name,
        )
        missiontype.delete()
        return DeleteMissionType(missiontype=missiontype)


# ===== Person =====
class PersonInput(graphene.InputObjectType):
    uuid = graphene.ID()
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    institution_name = graphene.String()


class CreatePerson(graphene.Mutation):
    class Arguments:
        first_name = graphene.String()
        last_name = graphene.String()
        institution_name = graphene.String()

    person = graphene.Field(PersonNode)

    def mutate(self, info, first_name, last_name, institution_name):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
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

    person = graphene.Field(PersonNode)

    def mutate(self, info, uuid, first_name, last_name, institution_name):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        person = Person.objects.get(uuid=uuid)
        person.first_name = first_name
        person.last_name = last_name
        person.institution_name = institution_name
        person.save()
        return UpdatePerson(person=person)


class DeletePerson(graphene.Mutation):
    class Arguments:
        uuid = graphene.String()

    person = graphene.Field(PersonNode)

    def mutate(self, info, uuid):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        person = Person.objects.get(uuid=uuid)
        person.delete()
        return DeletePerson(person=person)


# ===== PlatformType =====
class PlatformTypeInput(graphene.InputObjectType):
    platformtype_name = graphene.String(required=True)


class CreatePlatformType(graphene.Mutation):
    class Arguments:
        platformtype_name = graphene.String()

    platformtype = graphene.Field(PlatformTypeNode)

    def mutate(self, info, platformtype_name):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        platformtype = PlatformType.objects.create(
            platformtype_name=platformtype_name,
        )
        platformtype.save()
        return CreatePlatformType(platformtype=platformtype)


class UpdatePlatformType(graphene.Mutation):
    class Arguments:
        platformtype_name = graphene.String(required=True)
        new_platformtype_name = graphene.String(required=True)

    platformtype = graphene.Field(PlatformTypeNode)

    def mutate(self, info, platformtype_name, new_platformtype_name):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        platformtype = PlatformType.objects.get(
            platformtype_name=platformtype_name,
        )
        platformtype.platformtype_name = new_platformtype_name
        platformtype.save()
        return UpdatePlatformType(platformtype=platformtype)


class DeletePlatformType(graphene.Mutation):
    class Arguments:
        platformtype_name = graphene.String()

    platformtype = graphene.Field(PlatformTypeNode)

    def mutate(self, info, platformtype_name):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        platformtype = PlatformType.objects.get(
            platformtype_name=platformtype_name,
        )
        platformtype.delete()
        return DeletePlatformType(platformtype=platformtype)


# ===== Platform =====
class PlatformInput(graphene.InputObjectType):
    platform_name = graphene.String(required=True)
    platformtypes = graphene.List(PlatformTypeInput)
    operator_org_name = graphene.String(required=True)


class CreatePlatform(graphene.Mutation):
    class Arguments:
        input = PlatformInput(required=True)

    platform = graphene.Field(PlatformNode)

    def mutate(self, info, input):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        for platformtype in input.platformtypes:
            platformtype, _ = PlatformType.objects.get_or_create(
                platformtype_name=platformtype.platformtype_name
            )
        platform = Platform.objects.create(
            platform_name=input.platform_name,
            platform_type=platformtype,
            operator_org_name=input.operator_org_name,
        )
        platform.save()
        return CreatePlatform(platform=platform)


class UpdatePlatform(graphene.Mutation):
    class Arguments:
        platform_name = graphene.String(required=True)
        new_platform_name = graphene.String()
        new_operator_org_name = graphene.String()

    platform = graphene.Field(PlatformNode)

    def mutate(self, info, platform_name, new_platform_name, new_operator_org_name):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        platform = Platform.objects.get(
            platform_name=platform_name,
        )
        platform.platform_name = new_platform_name
        platform.operator_org_name = new_operator_org_name
        platform.save()
        return UpdatePlatform(platform=platform)


class DeletePlatform(graphene.Mutation):
    class Arguments:
        platform_name = graphene.String()

    platform = graphene.Field(PlatformNode)

    def mutate(self, info, platform_name):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        platform = Platform.objects.get(
            platform_name=platform_name,
        )
        platform.delete()
        return DeletePlatform(platform=platform)


# ===== SensorType =====
class SensorTypeInput(graphene.InputObjectType):
    sensortype_name = graphene.String(required=True)


class CreateSensorType(graphene.Mutation):
    class Arguments:
        sensortype_name = graphene.String()

    sensortype = graphene.Field(SensorTypeNode)

    def mutate(self, info, sensortype_name):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        sensortype = SensorType.objects.create(
            sensortype_name=sensortype_name,
        )
        sensortype.save()
        return CreateSensorType(sensortype=sensortype)


class UpdateSensorType(graphene.Mutation):
    class Arguments:
        sensortype_name = graphene.String(required=True)
        new_sensortype_name = graphene.String(required=True)

    sensortype = graphene.Field(SensorTypeNode)

    def mutate(self, info, sensortype_name, new_sensortype_name):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        sensortype = SensorType.objects.get(
            sensortype_name=sensortype_name,
        )
        sensortype.sensortype_name = new_sensortype_name
        sensortype.save()
        return UpdateSensorType(sensortype=sensortype)


class DeleteSensorType(graphene.Mutation):
    class Arguments:
        sensortype_name = graphene.String()

    sensortype = graphene.Field(SensorTypeNode)

    def mutate(self, info, sensortype_name):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        sensortype = SensorType.objects.get(
            sensortype_name=sensortype_name,
        )
        sensortype.delete()
        return DeleteSensorType(sensortype=sensortype)


# =====


class Mutation(graphene.ObjectType):
    create_missiontype = CreateMissionType.Field()
    update_missiontype = UpdateMissionType.Field()
    delete_missiontype = DeleteMissionType.Field()

    create_person = CreatePerson.Field()
    update_person = UpdatePerson.Field()
    delete_person = DeletePerson.Field()

    create_platformtype = CreatePlatformType.Field()
    update_platformtype = UpdatePlatformType.Field()
    delete_platformtype = DeletePlatformType.Field()

    create_platform = CreatePlatform.Field()
    update_platform = UpdatePlatform.Field()
    delete_platform = DeletePlatform.Field()

    create_sensortype = CreateSensorType.Field()
    update_sensortype = UpdateSensorType.Field()
    delete_sensortype = DeleteSensorType.Field()


schema = graphene.Schema(query=Query, mutation=Mutation, auto_camelcase=False)
