import graphene
from dateutil.parser import parse
from graphene_django import DjangoObjectType as DjangoObjectNode
from graphene_django.debug import DjangoDebug
from graphene_gis import scalars
from graphene_gis.converter import gis_converter
from graphql import GraphQLError

from smdb.models import (
    Citation,
    Compilation,
    DataArchival,
    Expedition,
    Mission,
    MissionType,
    Note,
    Person,
    Platform,
    PlatformType,
    Sensor,
    SensorType,
)


class MissionTypeNode(DjangoObjectNode):
    class Meta:
        model = MissionType
        fields = ("uuid", "name")


class PersonNode(DjangoObjectNode):
    class Meta:
        model = Person
        fields = ("uuid", "first_name", "last_name", "institution_name")


class PlatformTypeNode(DjangoObjectNode):
    class Meta:
        model = PlatformType
        fields = ("uuid", "name")


class PlatformNode(DjangoObjectNode):
    class Meta:
        model = Platform
        fields = (
            "uuid",
            "name",
            "operator_org_name",
            "platformtype",
        )


class SensorTypeNode(DjangoObjectNode):
    class Meta:
        model = SensorType
        fields = ("uuid", "name")


class SensorNode(DjangoObjectNode):
    class Meta:
        model = Sensor
        fields = (
            "uuid",
            "sensortype",
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


class MissionNode(DjangoObjectNode):
    class Meta:
        model = Mission
        fields = (
            "uuid",
            "mission_name",
            "grid_bounds",
            "expedition",
            "missiontype",
            "platform",
            "start_date",
            "end_date",
            "start_depth",
            "start_point",
            "quality_comment",
            "repeat_survey",
            "comment",
            "notes_filename",
            "region_name",
            "site_detail",
            "thumbnail_filename",
            "kml_filename",
            "compilation",
            "update_status",
            "sensors",
            "data_archivals",
            "citations",
        )


class DataArchivalNode(DjangoObjectNode):
    class Meta:
        model = DataArchival
        fields = (
            "uuid",
            "missions",
            "doi",
            "archival_db_name",
        )


class CitationNode(DjangoObjectNode):
    class Meta:
        model = Citation
        fields = (
            "uuid",
            "missions",
            "doi",
            "full_reference",
        )


class NoteNode(DjangoObjectNode):
    class Meta:
        model = Note
        fields = (
            "uuid",
            "text",
            "mission",
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
    all_missions = graphene.List(MissionNode)
    all_dataarchivals = graphene.List(DataArchivalNode)
    all_citations = graphene.List(CitationNode)
    all_notes = graphene.List(NoteNode)

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

    def resolve_all_missions(root, info):
        return Mission.objects.all()

    def resolve_all_dataarchivals(root, info):
        return DataArchival.objects.all()

    def resolve_all_citations(root, info):
        return Citation.objects.all()

    def resolve_all_notes(root, info):
        return Note.objects.all()

    # Specialized queries
    def resolve_missiontype_by_name(root, info, name):
        try:
            return MissionType.objects.get(name=name)
        except MissionType.DoesNotExist:
            return None

    def resolve_expedition_by_name(root, info, expd_name):
        try:
            return Expedition.objects.get(expd_name=expd_name)
        except Expedition.DoesNotExist:
            return None


# https://medium.com/analytics-vidhya/graphql-with-django-simple-yet-powerful-crud-part-2-bacce3668e35
# ===== MissionType =====
class MissionTypeInput(graphene.InputObjectType):
    name = graphene.String(required=True)


class CreateMissionType(graphene.Mutation):
    class Arguments:
        name = graphene.String()

    missiontype = graphene.Field(MissionTypeNode)

    def mutate(self, info, name):
        if not info.context.user.is_authenticated:
            raise GraphQLError("You must be logged in")
        missiontype = MissionType.objects.create(
            name=name,
        )
        missiontype.save()
        return CreateMissionType(missiontype=missiontype)


class UpdateMissionType(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        new_name = graphene.String(required=True)

    missiontype = graphene.Field(MissionTypeNode)

    def mutate(self, info, name, new_name):
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        missiontype = MissionType.objects.get(
            name=name,
        )
        missiontype.name = new_name
        missiontype.save()
        return UpdateMissionType(missiontype=missiontype)


class DeleteMissionType(graphene.Mutation):
    class Arguments:
        name = graphene.String()

    missiontype = graphene.Field(MissionTypeNode)

    def mutate(self, info, name):
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        missiontype = MissionType.objects.get(
            name=name,
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
        if not info.context.user.is_authenticated:  # pragma: no cover
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
        if not info.context.user.is_authenticated:  # pragma: no cover
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
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        person = Person.objects.get(uuid=uuid)
        person.delete()
        return DeletePerson(person=person)


# ===== PlatformType =====
class PlatformTypeInput(graphene.InputObjectType):
    name = graphene.String(required=True)


class CreatePlatformType(graphene.Mutation):
    class Arguments:
        name = graphene.String()

    platformtype = graphene.Field(PlatformTypeNode)

    def mutate(self, info, name):
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        platformtype = PlatformType.objects.create(
            name=name,
        )
        platformtype.save()
        return CreatePlatformType(platformtype=platformtype)


class UpdatePlatformType(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        new_name = graphene.String(required=True)

    platformtype = graphene.Field(PlatformTypeNode)

    def mutate(self, info, name, new_name):
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        platformtype = PlatformType.objects.get(
            name=name,
        )
        platformtype.name = new_name
        platformtype.save()
        return UpdatePlatformType(platformtype=platformtype)


class DeletePlatformType(graphene.Mutation):
    class Arguments:
        name = graphene.String()

    platformtype = graphene.Field(PlatformTypeNode)

    def mutate(self, info, name):
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        platformtype = PlatformType.objects.get(
            name=name,
        )
        platformtype.delete()
        return DeletePlatformType(platformtype=platformtype)


# ===== Platform =====
class PlatformInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    platformtype = graphene.Field(PlatformTypeInput)
    operator_org_name = graphene.String()


class CreatePlatform(graphene.Mutation):
    class Arguments:
        input = PlatformInput(required=True)

    platform = graphene.Field(PlatformNode)

    def mutate(self, info, input):
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        platformtype, _ = PlatformType.objects.get_or_create(
            name=input.platformtype.name
        )
        platform = Platform.objects.create(
            name=input.name,
            platformtype=platformtype,
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
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        platform = Platform.objects.get(uuid=uuid)
        platformtype, _ = PlatformType.objects.get_or_create(
            name=input.platformtype.name
        )
        platform.platformtype = platformtype
        platform.name = input.name
        platform.operator_org_name = input.operator_org_name
        platform.save()
        return UpdatePlatform(platform=platform)


class DeletePlatform(graphene.Mutation):
    class Arguments:
        uuid = graphene.ID()

    platform = graphene.Field(PlatformNode)

    def mutate(self, info, uuid):
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        platform = Platform.objects.get(uuid=uuid)
        platform.delete()
        return DeletePlatform(platform=platform)


# ===== SensorType =====
class SensorTypeInput(graphene.InputObjectType):
    name = graphene.String(required=True)


class CreateSensorType(graphene.Mutation):
    class Arguments:
        name = graphene.String()

    sensortype = graphene.Field(SensorTypeNode)

    def mutate(self, info, name):
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        sensortype = SensorType.objects.create(
            name=name,
        )
        sensortype.save()
        return CreateSensorType(sensortype=sensortype)


class UpdateSensorType(graphene.Mutation):
    class Arguments:
        name = graphene.String(required=True)
        new_name = graphene.String(required=True)

    sensortype = graphene.Field(SensorTypeNode)

    def mutate(self, info, name, new_name):
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        sensortype = SensorType.objects.get(
            name=name,
        )
        sensortype.name = new_name
        sensortype.save()
        return UpdateSensorType(sensortype=sensortype)


class DeleteSensorType(graphene.Mutation):
    class Arguments:
        name = graphene.String()

    sensortype = graphene.Field(SensorTypeNode)

    def mutate(self, info, name):
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        sensortype = SensorType.objects.get(
            name=name,
        )
        sensortype.delete()
        return DeleteSensorType(sensortype=sensortype)


# ===== Sensor =====
class SensorInput(graphene.InputObjectType):
    sensortype = graphene.Field(SensorTypeInput)
    model_name = graphene.String()
    comment = graphene.String()
    # missions is many-to-many, input will happen from Mission
    # missions = graphene.List(MissionInput)


class CreateSensor(graphene.Mutation):
    class Arguments:
        input = SensorInput(required=True)

    sensor = graphene.Field(SensorNode)

    def mutate(self, info, input):
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        sensortype, _ = SensorType.objects.get_or_create(name=input.sensortype.name)
        sensor = Sensor.objects.create(
            sensortype=sensortype,
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
        if not info.context.user.is_authenticated:  # pragma: no cover
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
        if not info.context.user.is_authenticated:  # pragma: no cover
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
        if not info.context.user.is_authenticated:  # pragma: no cover
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
        if not info.context.user.is_authenticated:  # pragma: no cover
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
        if not info.context.user.is_authenticated:  # pragma: no cover
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
        if not info.context.user.is_authenticated:  # pragma: no cover
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
        if not info.context.user.is_authenticated:  # pragma: no cover
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
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        compilation = Compilation.objects.get(uuid=uuid)
        compilation.delete()
        return DeleteCompilation(compilation=compilation)


# ===== Mission =====
class MissionInput(graphene.InputObjectType):
    mission_name = graphene.String(required=True)
    grid_bounds = graphene.Field(graphene.String, to=scalars.PolygonScalar())
    expedition = graphene.Field(ExpeditionInput, required=True)
    missiontype = graphene.Field(MissionTypeInput)
    platform = graphene.Field(PlatformInput)
    start_date = graphene.String()
    end_date = graphene.String()
    start_depth = graphene.Float()
    start_point = graphene.Field(graphene.String, to=scalars.PointScalar())
    quality_comment = graphene.String()
    repeat_survey = graphene.Boolean()
    comment = graphene.String()
    notes_filename = graphene.String()
    region_name = graphene.String()
    site_detail = graphene.String()
    thumbnail_filename = graphene.String()
    kml_filename = graphene.String()
    compilation = graphene.Field(CompilationInput)
    update_status = graphene.Int()
    sensors = graphene.List(SensorInput)
    data_archivals = graphene.List(lambda: DataArchivalInput)
    citations = graphene.List(lambda: CitationInput)


class CreateMission(graphene.Mutation):
    class Arguments:
        input = MissionInput(required=True)

    mission = graphene.Field(MissionNode)

    def mutate(self, info, input):
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")

        # DRY warning - these calls repeated in UpdateMission()
        expedition, _ = Expedition.objects.get_or_create(
            expd_name=input.expedition.expd_name,
        )
        missiontype, _ = MissionType.objects.get_or_create(
            name=input.missiontype.name,
        )
        platformtype, _ = PlatformType.objects.get_or_create(
            name=input.platform.platformtype.name,
        )
        platform, _ = Platform.objects.get_or_create(
            name=input.platform.name,
            platformtype=platformtype,
        )
        sensors = []
        for sensor_input in input.sensors or ():
            sensortype, _ = SensorType.objects.get_or_create(
                name=sensor_input.sensortype.name,
            )
            sensor, _ = Sensor.objects.get_or_create(
                comment=sensor_input.comment,
                model_name=sensor_input.model_name,
                sensortype=sensortype,
            )
            sensors.append(sensor)

        compilation, _ = Compilation.objects.get_or_create(
            compilation_dir_name=input.compilation.compilation_dir_name,
        )
        data_archivals = []
        for data_archival_input in input.data_archivals or ():
            data_archival, _ = DataArchival.objects.get_or_create(
                doi=data_archival_input.doi,
                archival_db_name=data_archival_input.archival_db_name,
            )
            data_archivals.append(data_archival)
        citations = []
        for citation_input in input.citations or ():
            citation, _ = Citation.objects.get_or_create(
                doi=citation_input.doi,
                full_reference=citation_input.full_reference,
            )
            citations.append(citation)
        # End DRY warning

        mission = Mission.objects.create(
            mission_name=input.mission_name,
            grid_bounds=input.grid_bounds,
            expedition=expedition,
            missiontype=missiontype,
            platform=platform,
            start_date=parse(input.start_date),
            end_date=parse(input.end_date),
            start_depth=input.start_depth,
            start_point=input.start_point,
            quality_comment=input.quality_comment,
            repeat_survey=input.repeat_survey,
            comment=input.comment,
            notes_filename=input.notes_filename,
            region_name=input.region_name,
            site_detail=input.site_detail,
            thumbnail_filename=input.thumbnail_filename,
            kml_filename=input.kml_filename,
            update_status=input.update_status,
            compilation=compilation,
        )
        mission.sensors.set(sensors)
        mission.data_archivals.set(data_archivals)
        mission.citations.set(citations)
        mission.save()
        return CreateMission(mission=mission)


class UpdateMission(graphene.Mutation):
    class Arguments:
        uuid = graphene.ID()
        input = MissionInput(required=True)

    mission = graphene.Field(MissionNode)

    def mutate(self, info, uuid, input):
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")

        # DRY warning - these calls repeated in CreateMission()
        expedition, _ = Expedition.objects.get_or_create(
            expd_name=input.expedition.expd_name,
        )
        missiontype, _ = MissionType.objects.get_or_create(
            name=input.missiontype.name,
        )
        platformtype, _ = PlatformType.objects.get_or_create(
            name=input.platform.platformtype.name,
        )
        platform, _ = Platform.objects.get_or_create(
            name=input.platform.name,
            platformtype=platformtype,
        )
        sensors = []
        for sensor_input in input.sensors or ():
            sensortype, _ = SensorType.objects.get_or_create(
                name=sensor_input.sensortype.name,
            )
            sensor, _ = Sensor.objects.get_or_create(
                comment=sensor_input.comment,
                model_name=sensor_input.model_name,
                sensortype=sensortype,
            )
            sensors.append(sensor)
        compilation, _ = Compilation.objects.get_or_create(
            compilation_dir_name=input.compilation.compilation_dir_name,
        )
        data_archivals = []
        for data_archival_input in input.data_archivals or ():
            data_archival, _ = DataArchival.objects.get_or_create(
                doi=data_archival_input.doi,
                archival_db_name=data_archival_input.archival_db_name,
            )
            data_archivals.append(data_archival)
        citations = []
        for citation_input in input.citations or ():
            citation, _ = Citation.objects.get_or_create(
                doi=citation_input.doi,
                full_reference=citation_input.full_reference,
            )
            citations.append(citation)
        # End DRY warning

        mission = Mission.objects.get(uuid=uuid)
        mission.mission_name = input.mission_name
        mission.grid_bounds = input.grid_bounds
        mission.expedition = expedition
        mission.missiontype = missiontype
        mission.platform = platform
        mission.start_date = parse(input.start_date)
        mission.end_date = parse(input.end_date)
        mission.start_depth = input.start_depth
        mission.start_point = input.start_point
        mission.quality_comment = input.quality_comment
        mission.repeat_survey = input.repeat_survey
        mission.comment = input.comment
        mission.notes_filename = input.notes_filename
        mission.region_name = input.region_name
        mission.site_detail = input.site_detail
        mission.thumbnail_filename = input.thumbnail_filename
        mission.kml_filename = input.kml_filename
        mission.update_status = input.update_status
        mission.compilation = compilation
        mission.sensors.set(sensors)
        mission.data_archivals.set(data_archivals)
        mission.citations.set(citations)
        mission.save()
        return UpdateMission(mission=mission)


class DeleteMission(graphene.Mutation):
    class Arguments:
        uuid = graphene.ID()

    mission = graphene.Field(MissionNode)

    def mutate(self, info, uuid):
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        mission = Mission.objects.get(uuid=uuid)
        mission.delete()
        return DeleteMission(mission=mission)


# ===== DataArchival =====
class DataArchivalInput(graphene.InputObjectType):
    missions = graphene.List(MissionInput)
    doi = graphene.String()
    archival_db_name = graphene.String()


class CreateDataArchival(graphene.Mutation):
    class Arguments:
        input = DataArchivalInput(required=True)

    dataarchival = graphene.Field(DataArchivalNode)

    def mutate(self, info, input):
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        missions = []
        for mission_input in input.missions:
            expedition, _ = Expedition.objects.get_or_create(
                expd_name=mission_input.expedition.expd_name,
                expd_path_name=mission_input.expedition.expd_path_name,
            )
            mission, _ = Mission.objects.get_or_create(
                mission_name=mission_input.mission_name,
                expedition=expedition,
            )
            missions.append(mission)
        dataarchival = DataArchival.objects.create(
            doi=input.doi,
            archival_db_name=input.archival_db_name,
        )
        dataarchival.missions.set(missions)
        dataarchival.save()
        return CreateDataArchival(dataarchival=dataarchival)


class UpdateDataArchival(graphene.Mutation):
    class Arguments:
        uuid = graphene.ID()
        input = DataArchivalInput(required=True)

    dataarchival = graphene.Field(DataArchivalNode)

    def mutate(self, info, uuid, input):
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        missions = []
        for mission_input in input.missions:
            expedition, _ = Expedition.objects.get_or_create(
                expd_name=mission_input.expedition.expd_name,
                expd_path_name=mission_input.expedition.expd_path_name,
            )
            mission, _ = Mission.objects.get_or_create(
                mission_name=mission_input.mission_name,
                expedition=expedition,
            )
            missions.append(mission)

        dataarchival = DataArchival.objects.get(uuid=uuid)
        dataarchival.doi = input.doi
        dataarchival.archival_db_name = input.archival_db_name
        dataarchival.missions.set(missions)
        dataarchival.save()
        return UpdateDataArchival(dataarchival=dataarchival)


class DeleteDataArchival(graphene.Mutation):
    class Arguments:
        uuid = graphene.ID()

    dataarchival = graphene.Field(DataArchivalNode)

    def mutate(self, info, uuid):

        dataarchival = DataArchival.objects.get(uuid=uuid)
        dataarchival.delete()
        return DeleteDataArchival(dataarchival=dataarchival)


# ===== Citation =====
class CitationInput(graphene.InputObjectType):
    missions = graphene.List(MissionInput)
    doi = graphene.String()
    full_reference = graphene.String()


class CreateCitation(graphene.Mutation):
    class Arguments:
        input = CitationInput(required=True)

    citation = graphene.Field(CitationNode)

    def mutate(self, info, input):
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        missions = []
        for mission_input in input.missions:
            expedition, _ = Expedition.objects.get_or_create(
                expd_name=mission_input.expedition.expd_name,
                expd_path_name=mission_input.expedition.expd_path_name,
            )
            mission, _ = Mission.objects.get_or_create(
                mission_name=mission_input.mission_name,
                expedition=expedition,
            )
            missions.append(mission)
        citation = Citation.objects.create(
            doi=input.doi,
            full_reference=input.full_reference,
        )
        citation.missions.set(missions)
        citation.save()
        return CreateCitation(citation=citation)


class UpdateCitation(graphene.Mutation):
    class Arguments:
        uuid = graphene.ID()
        input = CitationInput(required=True)

    citation = graphene.Field(CitationNode)

    def mutate(self, info, uuid, input):
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        missions = []
        for mission_input in input.missions:
            expedition, _ = Expedition.objects.get_or_create(
                expd_name=mission_input.expedition.expd_name,
                expd_path_name=mission_input.expedition.expd_path_name,
            )
            mission, _ = Mission.objects.get_or_create(
                mission_name=mission_input.mission_name,
                expedition=expedition,
            )
            missions.append(mission)
        citation = Citation.objects.get(uuid=uuid)
        citation.doi = input.doi
        citation.full_reference = input.full_reference
        citation.missions.set(missions)
        citation.save()
        return UpdateCitation(citation=citation)


class DeleteCitation(graphene.Mutation):
    class Arguments:
        uuid = graphene.ID()

    citation = graphene.Field(CitationNode)

    def mutate(self, info, uuid):
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        citation = Citation.objects.get(uuid=uuid)
        citation.delete()
        return DeleteCitation(citation=citation)


# ===== Note =====
class NoteInput(graphene.InputObjectType):
    text = graphene.String()
    mission = graphene.Field(MissionInput)


class CreateNote(graphene.Mutation):
    class Arguments:
        input = NoteInput(required=True)

    note = graphene.Field(NoteNode)

    def mutate(self, info, input):
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        expedition, _ = Expedition.objects.get_or_create(
            expd_name=input.mission.expedition.expd_name,
            expd_path_name=input.mission.expedition.expd_path_name,
        )
        mission, _ = Mission.objects.get_or_create(
            mission_name=input.mission.mission_name,
            expedition=expedition,
        )
        note = Note.objects.create(
            text=input.text,
            mission=mission,
        )
        note.save()
        return CreateNote(note=note)


class UpdateNote(graphene.Mutation):
    class Arguments:
        uuid = graphene.ID()
        input = NoteInput(required=True)

    note = graphene.Field(NoteNode)

    def mutate(self, info, uuid, input):
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        expedition, _ = Expedition.objects.get_or_create(
            expd_name=input.mission.expedition.expd_name,
            expd_path_name=input.mission.expedition.expd_path_name,
        )
        mission, _ = Mission.objects.get_or_create(
            mission_name=input.mission.mission_name,
            expedition=expedition,
        )
        note = Note.objects.get(uuid=uuid)
        note.text = input.text
        note.mission = mission
        note.save()
        return UpdateNote(note=note)


class DeleteNote(graphene.Mutation):
    class Arguments:
        uuid = graphene.ID()

    note = graphene.Field(NoteNode)

    def mutate(self, info, uuid):
        if not info.context.user.is_authenticated:  # pragma: no cover
            raise GraphQLError("You must be logged in")
        note = Note.objects.get(uuid=uuid)
        note.delete()
        return DeleteNote(note=note)


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

    create_mission = CreateMission.Field()
    update_mission = UpdateMission.Field()
    delete_mission = DeleteMission.Field()

    create_dataarchival = CreateDataArchival.Field()
    update_dataarchival = UpdateDataArchival.Field()
    delete_dataarchival = DeleteDataArchival.Field()

    create_citation = CreateCitation.Field()
    update_citation = UpdateCitation.Field()
    delete_citation = DeleteCitation.Field()

    create_note = CreateNote.Field()
    update_note = UpdateNote.Field()
    delete_note = DeleteNote.Field()


schema = graphene.Schema(query=Query, mutation=Mutation, auto_camelcase=False)
