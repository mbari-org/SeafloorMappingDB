import graphene
from dateutil.parser import parse
from graphene_django import DjangoObjectType as DjangoObjectNode
from graphene_django.debug import DjangoDebug
from graphene_gis import scalars
from graphene_gis.converter import gis_converter
from graphql import GraphQLError

from smdb.models import (
    Compilation,
    Expedition,
    MissionType,
    Person,
    Platform,
    PlatformType,
    Sensor,
    SensorType,
)


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


class SensorNode(DjangoObjectNode):
    class Meta:
        model = Sensor
        fields = (
            "uuid",
            "sensor_type",
            "model_name",
            "comment",
            "missions",
        )


class ExpeditionNode(DjangoObjectNode):
    class Meta:
        model = Expedition
        fields = (
            "uuid",
            "expd_name",
            "start_date",
            "end_date",
            "investigator",
            "chiefscientist",
            "expd_path_name",
            "expd_db_id",
        )


class CompilationNode(DjangoObjectNode):
    class Meta:
        model = Compilation
        fields = (
            "uuid",
            "compilation_dir_name",
            "grid_bounds",
            "compilation_path_name",
            "navadjust_dir_path",
            "figures_dir_path",
            "comment",
            "thumbnail_filename",
            "kml_filename",
            "proc_datalist_filename",
            "update_status",
        )


class Query(graphene.ObjectType):
    debug = graphene.Field(DjangoDebug, name="_debug")
    all_missiontypes = graphene.List(MissionTypeNode)
    all_persons = graphene.List(PersonNode)
    all_platformtypes = graphene.List(PlatformTypeNode)
    all_platforms = graphene.List(PlatformNode)
    all_sensortypes = graphene.List(SensorTypeNode)
    all_sensors = graphene.List(SensorNode)
    all_expeditions = graphene.List(ExpeditionNode)
    all_compilations = graphene.List(CompilationNode)

    missiontype_by_name = graphene.Field(
        MissionTypeNode, name=graphene.String(required=True)
    )

    expedition_by_name = graphene.Field(
        ExpeditionNode, expd_name=graphene.String(required=True)
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

    def resolve_all_sensors(root, info):
        return Sensor.objects.all()

    def resolve_all_expeditions(root, info):
        return Expedition.objects.all()

    def resolve_all_compilations(root, info):
        return Compilation.objects.all()

    # Specialized queries
    def resolve_missiontype_by_name(root, info, name):
        try:
            return MissionType.objects.get(missiontype_name=name)
        except MissionType.DoesNotExist:
            return None

    def resolve_expedition_by_name(root, info, expd_name):
        try:
            return Expedition.objects.get(expd_name=expd_name)
        except Expedition.DoesNotExist:
            return None

    def resolve_compilation_by_name(root, info, expd_name):
        try:
            return Compilation.objects.get(expd_name=expd_name)
        except Compilation.DoesNotExist:
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
    first_name = graphene.String(required=True)
    last_name = graphene.String(required=True)
    institution_name = graphene.String()


class CreatePerson(graphene.Mutation):
    class Arguments:
        input = PersonInput(required=True)

        first_name = graphene.String()
        last_name = graphene.String()
        institution_name = graphene.String()

    person = graphene.Field(PersonNode)

    def mutate(self, info, input):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        person = Person.objects.create(
            first_name=input.first_name,
            last_name=input.last_name,
            institution_name=input.institution_name,
        )
        person.save()
        return CreatePerson(person=person)


class UpdatePerson(graphene.Mutation):
    class Arguments:
        uuid = graphene.ID(required=True)
        input = PersonInput(required=True)

    person = graphene.Field(PersonNode)

    def mutate(self, info, uuid, input):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        person = Person.objects.get(uuid=uuid)
        person.first_name = input.first_name
        person.last_name = input.last_name
        person.institution_name = input.institution_name
        person.save()
        return UpdatePerson(person=person)


class DeletePerson(graphene.Mutation):
    class Arguments:
        uuid = graphene.ID()

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
        uuid = graphene.ID()
        input = PlatformInput(required=True)

    platform = graphene.Field(PlatformNode)

    def mutate(self, info, uuid, input):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        platform = Platform.objects.get(uuid=uuid)
        for platformtype_input in input.platformtypes:
            platformtype, _ = PlatformType.objects.get_or_create(
                platformtype_name=platformtype_input.platformtype_name
            )
            platform.platform_type = platformtype
            break  # Assign first platformtype_input encountered
        platform.platform_name = input.platform_name
        platform.operator_org_name = input.operator_org_name
        platform.save()
        return UpdatePlatform(platform=platform)


class DeletePlatform(graphene.Mutation):
    class Arguments:
        uuid = graphene.ID()

    platform = graphene.Field(PlatformNode)

    def mutate(self, info, uuid):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        platform = Platform.objects.get(uuid=uuid)
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


# ===== Sensor =====
class MissionInput(graphene.InputObjectType):

    mission_name = graphene.String(required=True)
    grid_bounds = graphene.Field(graphene.String, to=scalars.PolygonScalar())

    """
    grid_bounds = models.PolygonField(
        srid=4326, spatial_index=True, blank=True, null=True
    )
    expedition = models.ForeignKey(
        Expedition, on_delete=models.CASCADE, blank=True, null=True
    )
    missiontype = models.ForeignKey(
        MissionType, on_delete=models.CASCADE, blank=True, null=True
    )
    platform = models.ForeignKey(
        Platform, on_delete=models.CASCADE, blank=True, null=True
    )
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    start_depth = models.FloatField(blank=True, null=True)
    start_point = models.PointField(
        srid=4326, spatial_index=True, dim=2, blank=True, null=True
    )
    quality_comment = models.TextField(blank=True, null=True)
    repeat_survey = models.BooleanField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    notes_filename = models.CharField(max_length=128, db_index=True, null=True)
    region_name = models.CharField(max_length=128, db_index=True)
    site_detail = models.CharField(max_length=128, db_index=True)
    thumbnail_filename = models.CharField(max_length=128, db_index=True)
    kml_filename = models.CharField(max_length=128, db_index=True)
    compilation = models.ForeignKey(
        Compilation, on_delete=models.CASCADE, blank=True, null=True
    )
    update_status = models.IntegerField(blank=True, null=True)
    sensors = models.ManyToManyField(Sensor)
    data_archivals = models.ManyToManyField("DataArchival", blank=True)
    citations = models.ManyToManyField("Citation", blank=True)
    """


class SensorInput(graphene.InputObjectType):
    sensortypes = graphene.List(SensorTypeInput)
    model_name = graphene.String()
    comment = graphene.String()
    # missions is many-to-many, input will happen from Mission
    # missions = graphene.List(MissionInput)


class CreateSensor(graphene.Mutation):
    class Arguments:
        input = SensorInput(required=True)

    sensor = graphene.Field(SensorNode)

    def mutate(self, info, input):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        for sensortype in input.sensortypes:
            sensortype, _ = SensorType.objects.get_or_create(
                sensortype_name=sensortype.sensortype_name
            )
        sensor = Sensor.objects.create(
            sensor_type=sensortype,
            model_name=input.model_name,
            comment=input.comment,
        )
        sensor.save()
        return CreateSensor(sensor=sensor)


class UpdateSensor(graphene.Mutation):
    class Arguments:
        uuid = graphene.ID()
        input = SensorInput(required=True)

    sensor = graphene.Field(SensorNode)

    def mutate(self, info, uuid, input):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        sensor = Sensor.objects.get(uuid=uuid)
        sensor.model_name = input.model_name
        sensor.comment = input.comment
        sensor.save()
        return UpdateSensor(sensor=sensor)


class DeleteSensor(graphene.Mutation):
    class Arguments:
        uuid = graphene.ID()

    sensor = graphene.Field(SensorNode)

    def mutate(self, info, uuid):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        sensor = Sensor.objects.get(uuid=uuid)
        sensor.delete()
        return DeleteSensor(sensor=sensor)


# ===== Expedition =====
class ExpeditionInput(graphene.InputObjectType):
    expd_name = graphene.String()
    start_date_iso = graphene.String()
    end_date_iso = graphene.String()
    investigator = graphene.Field(PersonInput)
    chiefscientist = graphene.Field(PersonInput)
    expd_path_name = graphene.String()
    expd_db_id = graphene.Int()


class CreateExpedition(graphene.Mutation):
    class Arguments:
        input = ExpeditionInput(required=True)

    expedition = graphene.Field(ExpeditionNode)

    def mutate(self, info, input):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")

        investigator, _ = Person.objects.get_or_create(
            first_name=input.investigator.first_name,
            last_name=input.investigator.last_name,
        )
        chiefscientist, _ = Person.objects.get_or_create(
            first_name=input.chiefscientist.first_name,
            last_name=input.chiefscientist.last_name,
        )
        expedition = Expedition.objects.create(
            expd_name=input.expd_name,
            start_date=parse(input.start_date_iso),
            end_date=parse(input.end_date_iso),
            investigator=investigator,
            chiefscientist=chiefscientist,
            expd_path_name=input.expd_path_name,
            expd_db_id=input.expd_db_id,
        )
        expedition.save()
        return CreateExpedition(expedition=expedition)


class UpdateExpedition(graphene.Mutation):
    class Arguments:
        uuid = graphene.ID()
        input = ExpeditionInput(required=True)

    expedition = graphene.Field(ExpeditionNode)

    def mutate(self, info, uuid, input):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        investigator, _ = Person.objects.get_or_create(
            first_name=input.investigator.first_name,
            last_name=input.investigator.last_name,
        )
        chiefscientist, _ = Person.objects.get_or_create(
            first_name=input.chiefscientist.first_name,
            last_name=input.chiefscientist.last_name,
        )
        expedition = Expedition.objects.get(uuid=uuid)
        expedition.expd_name = input.expd_name
        expedition.start_date = parse(input.start_date_iso)
        expedition.end_date = parse(input.end_date_iso)
        expedition.investigator = investigator
        expedition.chiefscientist = chiefscientist
        expedition.expd_path_name = input.expd_path_name
        expedition.save()
        return UpdateExpedition(expedition=expedition)


class DeleteExpedition(graphene.Mutation):
    class Arguments:
        uuid = graphene.ID()

    expedition = graphene.Field(ExpeditionNode)

    def mutate(self, info, uuid):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        expedition = Expedition.objects.get(uuid=uuid)
        expedition.delete()
        return DeleteExpedition(expedition=expedition)


# ===== Compilation =====
class CompilationInput(graphene.InputObjectType):
    compilation_dir_name = graphene.String()
    grid_bounds = graphene.Field(graphene.String, to=scalars.PolygonScalar())
    compilation_path_name = graphene.String()
    navadjust_dir_path = graphene.String()
    figures_dir_path = graphene.String()
    comment = graphene.String()
    thumbnail_filename = graphene.String()
    kml_filename = graphene.String()
    proc_datalist_filename = graphene.String()
    update_status = graphene.Int()


class CreateCompilation(graphene.Mutation):
    class Arguments:
        input = CompilationInput(required=True)

    compilation = graphene.Field(CompilationNode)

    def mutate(self, info, input):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        compilation = Compilation.objects.create(
            compilation_dir_name=input.compilation_dir_name,
            grid_bounds=input.grid_bounds,
            compilation_path_name=input.compilation_path_name,
            navadjust_dir_path=input.navadjust_dir_path,
            figures_dir_path=input.figures_dir_path,
            comment=input.comment,
            thumbnail_filename=input.thumbnail_filename,
            kml_filename=input.kml_filename,
            proc_datalist_filename=input.proc_datalist_filename,
            update_status=input.update_status,
        )
        compilation.save()
        return CreateCompilation(compilation=compilation)


class UpdateCompilation(graphene.Mutation):
    class Arguments:
        uuid = graphene.ID()
        input = CompilationInput(required=True)

    compilation = graphene.Field(CompilationNode)

    def mutate(self, info, uuid, input):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        compilation = Compilation.objects.get(uuid=uuid)
        compilation.compilation_dir_name = input.compilation_dir_name
        compilation.grid_bounds = input.grid_bounds
        compilation.compilation_path_name = input.compilation_path_name
        compilation.navadjust_dir_path = input.navadjust_dir_path
        compilation.figures_dir_path = input.figures_dir_path
        compilation.comment = input.comment
        compilation.thumbnail_filename = input.thumbnail_filename
        compilation.kml_filename = input.kml_filename
        compilation.proc_datalist_filename = input.proc_datalist_filename
        compilation.update_status = input.update_status
        compilation.save()
        return UpdateCompilation(compilation=compilation)


class DeleteCompilation(graphene.Mutation):
    class Arguments:
        uuid = graphene.ID()

    compilation = graphene.Field(CompilationNode)

    def mutate(self, info, uuid):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        compilation = Compilation.objects.get(uuid=uuid)
        compilation.delete()
        return DeleteCompilation(compilation=compilation)


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

    create_sensor = CreateSensor.Field()
    update_sensor = UpdateSensor.Field()
    delete_sensor = DeleteSensor.Field()

    create_expedition = CreateExpedition.Field()
    update_expedition = UpdateExpedition.Field()
    delete_expedition = DeleteExpedition.Field()

    create_compilation = CreateCompilation.Field()
    update_compilation = UpdateCompilation.Field()
    delete_compilation = DeleteCompilation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation, auto_camelcase=False)
