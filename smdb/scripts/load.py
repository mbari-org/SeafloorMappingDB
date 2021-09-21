#!/usr/bin/python
"""
Scan SeafloorMapping share for data to load into smdb
"""

import os
import sys

import django

parentDir = os.path.join(os.path.dirname(__file__), "../")
sys.path.insert(0, parentDir)
os.environ["DJANGO_SETTINGS_MODULE"] = f"config.settings.{os.environ['BUILD_ENV']}"
django.setup()

import argparse  # noqa F402
import getpass  # noqa F402
import logging  # noqa F402
import math  # noqa F402
import re  # noqa F402
import subprocess  # noqa F402
from netCDF4 import Dataset  # noqa F402
from datetime import datetime  # noqa F402
from dateutil.parser import ParserError, parse  # noqa F402
from django.conf import settings  # noqa F402
from django.contrib.gis.geos import Polygon  # noqa F402
from PIL import Image, UnidentifiedImageError  # noqa F402
from smdb.models import Expedition, Mission, Note  # noqa F402
from subprocess import check_output, TimeoutExpired  # noqa F402
from time import time  # noqa F402

MBARI_DIR = "/mbari/SeafloorMapping/"

instructions = f"""
Can be run from smdb Docker environment thusly...
    First time - install necessary things:
        git clone git@github.com:mbari-org/SeafloorMappingDB.git
        cd SeafloorMappingDB
        export SMDB_HOME=$(pwd)
        export COMPOSE_FILE=$SMDB_HOME/smdb/local.yml
        docker-compose up -d
    Thereafter, on command line:
        cd SeafloorMappingDB
        export SMDB_HOME=$(pwd)
        export COMPOSE_FILE=$SMDB_HOME/smdb/local.yml
        docker-compose run --rm -u $UID -v /Volumes/SeafloorMapping:/mbari/SeafloorMapping django {__file__} -h
        -- or, on production --
        export COMPOSE_FILE=$SMDB_HOME/smdb/production.yml
        docker-compose run --rm -u $UID -v /mbari/SeafloorMapping:/mbari/SeafloorMapping django {__file__} -h
    From VS Code:
        - Mount smb://titan.shore.mbari.org/SeafloorMapping
        - Open zsh terminal, at ➜  /app/smdb prompt:
          scripts/load.py --help
          scripts/load.py -v --clobber # To reload database
          or use the "load.py" Debug launch configuration

"""


class BaseLoader:
    def __init__(self):
        self.logger = logging.getLogger("load")
        self._log_levels = (logging.WARN, logging.INFO, logging.DEBUG)
        self._log_strings = ("WARN", "INFO", "DEBUG")
        self.commandline = None
        self.exclude_files = []

    def process_command_line(self):
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawTextHelpFormatter,
            epilog=instructions,
        )
        parser.add_argument(
            "-v",
            "--verbose",
            type=int,
            choices=range(3),
            action="store",
            default=0,
            const=1,
            nargs="?",
            help="verbosity level: "
            + ", ".join([f"{i}: {v}" for i, v, in enumerate(self._log_strings)]),
        )
        parser.add_argument(
            "--clobber",
            action="store_true",
            help="Delete all Expeditions and Missions before loading",
        )
        parser.add_argument(
            "--exclude",
            action="store",
            help="Name of file containing Mission names to exclude",
            default="/etc/smdb/exclude.list",
        )
        parser.add_argument(
            "--regex",
            action="store",
            help="Load only ZTopo.grd files that have this regular expression in their path",
            default="\/(?P<yr>\d\d\d\d)(?P<mo>\d\d)(?P<da>\d\d)(?P<miss_seq>\S\S)\/",
        )
        parser.add_argument(
            "--bootstrap",
            action="store_true",
            help="Load initial Mission, Expedition and Notes data from file system - do not do notes load",
        )
        parser.add_argument(
            "--notes",
            action="store_true",
            help="Process the notes loaded by a bootstrap load - do not do bootstrap load",
        )
        parser.add_argument(
            "--mbsystem",
            action="store_true",
            help="Run the loading steps that require MB-System commands - do not do other load steps",
        )
        parser.add_argument(
            "--limit",
            action="store",
            type=int,
            help="Stop loading after this number of records",
        )
        parser.add_argument(
            "--noinput",
            action="store_true",
            help="Don't ask to confirm --clobber",
        )
        parser.add_argument(
            "--skipuntil_regex",
            action="store_true",
            help="Start bootstrap processing at --regex  provided",
        )
        parser.add_argument(
            "--skipuntil",
            action="store",
            help="Start processing at mission name provided",
        )

        self.args = parser.parse_args()  # noqa
        self.commandline = " ".join(sys.argv)

        # Override Django's logging so that we can setLevel() with --verbose
        logging.getLogger().handlers.clear()
        _handler = logging.StreamHandler()
        _formatter = logging.Formatter(
            "%(levelname)s %(asctime)s %(filename)s "
            "%(funcName)s():%(lineno)d %(message)s"
        )
        _handler.setFormatter(_formatter)
        if not self.logger.handlers:
            # Don't add handler for sub class
            self.logger.addHandler(_handler)
        self.logger.setLevel(self._log_levels[self.args.verbose])

        for line in open(self.args.exclude):
            if not line.startswith("#"):
                self.exclude_files.append(line.strip())

        self.logger.debug(
            "Using database at DATABASE_URL = %s", os.environ["DATABASE_URL"]
        )


class NoteParser(BaseLoader):
    BOUNDARY_DASHES = "------------------------------------"

    def filepaths(self):
        return Mission.objects.all().values_list("notes_filename", flat=True)

    def parse_texts(self):
        """Brute force parsing of Note text to grab information"""
        for note_count, note in enumerate(Note.objects.all()):
            self.logger.info(f"======== %d. %s ========", note_count, note.mission.name)
            comment_captured = False
            next_line_is_expd_db_id = False
            comment = ""
            for line in note.text.split("\n"):
                if not comment_captured:
                    comment += line + "\n"
                self.logger.debug(line)
                if line == self.BOUNDARY_DASHES and not comment_captured:
                    comment_captured = True
                    comment = comment.replace(self.BOUNDARY_DASHES, "")
                    note.mission.comment = comment.strip()
                    if note.mission.comment == "":
                        self.logger.warning(
                            "Empty comment for mission %s", note.mission
                        )
                    note.mission.save()

                if next_line_is_expd_db_id:
                    try:
                        note.mission.expedition.expd_db_id = int(line)
                    except ValueError:
                        self.logger.warning(
                            "Could not get expd_db_id for %s from Notes file %s",
                            note.mission.name,
                            note.mission.notes_filename,
                        )
                    note.mission.expedition.save()
                    next_line_is_expd_db_id = False
                if "ExpeditionID" in line:
                    self.logger.debug(line)
                    if expd_ma := re.match(r"ExpeditionID\s+(\d+)", line):
                        # ExpeditionID	6229
                        note.mission.expedition.expd_db_id = int(expd_ma.group(1))
                        note.mission.expedition.save()
                        next_line_is_expd_db_id = False
                    else:
                        next_line_is_expd_db_id = True

    def save_expd_name_from_comment(self):
        # It looks like the third line begins with an Expedition name
        for mission in Mission.objects.all():
            expd_name = ""
            self.logger.info("Saving expedition.name for mission: %s", mission)
            if not mission.comment:
                self.logger.warning("Empty comment for mission %s", mission)
                try:
                    if hasattr(Note.objects.get(mission=mission), "text"):
                        self.logger.debug(
                            "note.text = \n%s", Note.objects.get(mission=mission).text
                        )
                except Note.DoesNotExist:
                    self.logger.debug("No Note saved for mission %s", mission)
                continue
            for count, line in enumerate(mission.comment.split("\n")):
                if count > 1:
                    expd_name += line + " "
            mission.expedition.name = expd_name
            try:
                mission.expedition.save()
            except django.db.utils.DataError:
                self.logger.warning("Error saving expedition.name: %s", expd_name)


class MBSystem(BaseLoader):
    SSH_CMD = f"ssh {getpass.getuser()}@mb-system"
    TIMEOUT = 360  # Max seconds to retreive file from tertiary storage

    def sonar_start_time(self, sonar_file: str) -> datetime:
        cmd = f"{self.SSH_CMD} mbinfo -I {sonar_file}"
        start_line = False

        self.logger.debug("Executing %s", cmd)
        try:
            start_esec = time()
            lines = check_output(cmd.split(), timeout=self.TIMEOUT).decode().split("\n")
        except TimeoutExpired:
            self.logger.warning("Timeout for: %s", cmd)
            raise TimeoutExpired(cmd, self.TIMEOUT)
        for line in lines:
            if start_line:
                # Time:  03 18 2019 12:09:53.564998  JD77 (2019-03-18T12:09:53.564998)
                ma = re.match(
                    r"Time:.+\((\d\d\d\d\-\d\d-\d\dT\d\d:\d\d:\d\d\.\d+)\)",
                    line,
                )
                self.logger.debug(
                    "%4.2f seconds to scan %s", time() - start_esec, sonar_file
                )
                return parse(ma.group(1))
            if line == "Start of Data:":
                start_line = True
        raise ValueError(f"Could not find 'Start of Data' from: {cmd}")

    def sonar_end_time(self, sonar_file: str) -> datetime:
        cmd = f"{self.SSH_CMD} mbinfo -I {sonar_file}"
        end_line = False
        self.logger.debug("Executing %s", cmd)
        try:
            start_esec = time()
            lines = check_output(cmd.split(), timeout=self.TIMEOUT).decode().split("\n")
        except TimeoutExpired:
            self.logger.warning("Timeout for: %s", cmd)
            raise TimeoutExpired(cmd, self.TIMEOUT)
        for line in lines:
            if end_line:
                # Time:  03 18 2019 12:09:53.564998  JD77 (2019-03-18T12:09:53.564998)
                ma = re.match(
                    r"Time:.+\((\d\d\d\d\-\d\d-\d\dT\d\d:\d\d:\d\d\.\d+)\)", line
                )
                self.logger.debug(
                    "%4.2f seconds to scan %s", time() - start_esec, sonar_file
                )
                return parse(ma.group(1))
            if line == "End of Data:":
                end_line = True
        raise ValueError(f"Could not find 'End of Data' from: {cmd}")

    def first_sonar_time(self, path: str, datalist: str) -> datetime:
        with open(datalist) as fh:
            for line in fh.readlines():
                if line.startswith("#"):
                    continue
                item = line.split()[0].strip()
                if item.endswith("mb-1"):
                    return self.first_sonar_time(path, os.path.join(path, item))
                elif re.match(r".+\.mb\d\d", item):
                    return self.sonar_start_time(os.path.join(path, item))

    def last_sonar_time(self, path: str, datalist: str) -> datetime:
        last_sonar_item = None
        with open(datalist) as fh:
            for line in fh.readlines():
                if line.startswith("#"):
                    continue
                item = line.split()[0].strip()
                if item.endswith("mb-1") or re.match(r".+\.mb\d\d", item):
                    last_sonar_item = item
            if not last_sonar_item:
                raise ValueError(
                    "Did not find last_sonar_item for datalist %s",
                    datalist,
                )
            if last_sonar_item.endswith("mb-1"):
                return self.last_sonar_time(
                    path,
                    os.path.join(path, last_sonar_item),
                )
            elif re.match(r".+\.mb\d\d", last_sonar_item):
                return self.sonar_end_time(os.path.join(path, item))

    def process_missions(self):
        start_processing = True
        if self.args.skipuntil:
            start_processing = False
        for miss_count, mission in enumerate(
            Mission.objects.all().order_by("name"), start=1
        ):
            if self.args.skipuntil:
                if mission.name == self.args.skipuntil:
                    start_processing = True
            if not start_processing:
                continue
            try:
                self.logger.info(f"======== %d. %s ========", miss_count, mission)
                self.update_mission_times(mission)
            except (ParserError, FileNotFoundError) as e:
                self.logger.warning(e)
            if self.args.limit:
                if miss_count >= self.args.limit:
                    break

    def update_mission_times(self, mission: Mission):
        # Start with datalistp.mb-1 and recurse down
        # to find first and last sonar file and corresponding
        # first and last datetimes for the mission
        path = mission.expedition.expd_path_name
        datalist = os.path.join(path, "datalistp.mb-1")
        mission.start_date = self.first_sonar_time(path, datalist)
        mission.end_date = self.last_sonar_time(path, datalist)
        mission.save()
        self.logger.info(
            "Saved start & end: %s to %s", mission.start_date, mission.end_date
        )


class Scanner(BaseLoader):
    LOCATE_DB = "/etc/smdb/SeafloorMapping.db"

    def extent(self, ds, file):
        if "x" in ds.variables and "y" in ds.variables:
            X = "x"
            Y = "y"
        elif "lon" in ds.variables and "lat" in ds.variables:
            X = "lon"
            Y = "lat"
        else:
            raise ValueError(f"Did not find x/y nor lon/lat in file {file}")

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
        for point in grid_bounds[0]:
            self.logger.debug("Checking if point is on Earth: %s", point)
            lon, lat = point
            if lon < -180 or lon > 360:
                raise ValueError(
                    f"Bad longitude bounds ({str(grid_bounds)}) in file {file}"
                )
            if lat < -90 or lat > 90:
                raise ValueError(
                    f"Bad latitude bounds ({str(grid_bounds)}) in file {file}"
                )
            if math.isclose(lon, 0, abs_tol=1e-6):
                raise ValueError(
                    f"Near zero longitude bounds ({str(grid_bounds)}) in file {file}"
                )
            if math.isclose(lat, 0, abs_tol=1e-6):
                raise ValueError(
                    f"Near zero latitude bounds ({str(grid_bounds)}) in file {file}"
                )

        return grid_bounds

    def is_geographic(self, ds):
        if hasattr(ds, "description"):
            # More recent files have this attribute
            if "Projection: Geographic" in ds.description:
                return True
        elif hasattr(ds, "source"):
            # Older files have this attribute
            if "Projection: Geographic" in ds.source:
                return True
        else:
            self.logger.warning("% does not have attribute descrtion nor source", ds)

        return False

    def notes_filename(self, sm_dir):
        locate_cmd = f"locate -d {self.LOCATE_DB} -r '{sm_dir}.*Notes.txt$'"
        notes_file = None
        for txt_file in subprocess.getoutput(locate_cmd).split("\n"):
            if txt_file:
                self.logger.debug("Potential notes file: %s", txt_file)
                if "junk" in txt_file:
                    self.logger.debug(
                        "Skipping over Notes file found in junk dir: %s", txt_file
                    )
                    continue
                notes_file = txt_file

        if not notes_file:
            # Try parent directory
            parent_dir = os.path.abspath(os.path.join(sm_dir, ".."))
            locate_cmd = f"locate -d {self.LOCATE_DB} -r '{parent_dir}.*Notes.txt$'"
            for txt_file in subprocess.getoutput(locate_cmd).split("\n"):
                if txt_file:
                    self.logger.debug("Potential notes file: %s", txt_file)
                    notes_file = txt_file
        if not notes_file:
            # Try grandparent directory
            grandparent_dir = os.path.abspath(os.path.join(sm_dir, "../.."))
            locate_cmd = (
                f"locate -d {self.LOCATE_DB} -r '{grandparent_dir}.*Notes.txt$'"
            )
            for txt_file in subprocess.getoutput(locate_cmd).split("\n"):
                if txt_file:
                    self.logger.debug("Potential notes file: %s", txt_file)
                    notes_file = txt_file

        return notes_file

    def thumbnail_filename(self, sm_dir):
        locate_cmd = f"locate -d {self.LOCATE_DB} -r '{sm_dir}/ZTopoSlopeNav.jpg'"
        thumbnail_file = None
        for jpg_file in subprocess.getoutput(locate_cmd).split("\n"):
            self.logger.debug("Potential thumbnail file: %s", jpg_file)
            thumbnail_file = jpg_file

        return thumbnail_file

    def save_notes(self, mission):
        if not mission.notes_filename:
            raise FileExistsError(f"No Notes found for {mission}")
        note_text = ""
        with open(mission.notes_filename) as fh:
            try:
                for line_count, line in enumerate(fh.readlines()):
                    if "password" in line.lower():
                        # Blank out actual passwords
                        line = (
                            line.lower().split("password")[0] + "password: **********"
                        )
                    note_text += line
            except UnicodeDecodeError as e:
                self.logger.warning(
                    "Cannot read Notes file: %s", mission.notes_filename
                )
                raise FileExistsError(f"No Notes found for {mission}")

        if not note_text:
            raise FileExistsError(f"No Notes found for {mission}")

        note = Note(
            mission=mission,
            text=note_text,
        )
        note.save()
        self.logger.info(f"Saved %d lines of note text", line_count)

    def save_thumbnail(self, mission):
        if not mission.thumbnail_filename:
            raise FileExistsError(f"No thumbnail image found for {mission}")
        scale_factor = 8
        try:
            im = Image.open(mission.thumbnail_filename)
        except UnidentifiedImageError as e:
            self.logger.warning(f"{e}")
            return
        width, height = im.size
        nx = width // scale_factor
        ny = height // scale_factor
        new_im = im.resize((nx, ny))

        new_name = "_".join(
            mission.thumbnail_filename.replace(MBARI_DIR, "").split("/")
        )
        im_path = os.path.join(settings.MEDIA_ROOT, "thumbnails", new_name)
        new_im.save(im_path, "JPEG")
        mission.thumbnail_image = os.path.join("thumbnails", new_name)
        mission.save()
        self.logger.info(f"Saved thumbnail image of size %dx%s", nx, ny)


def run(*args):
    # Possible use: https://django-extensions.readthedocs.io/en/latest/runscript.html
    bl = BaseLoader()
    bl.process_command_line()
    bl.logger.debug("Arguments passed to run(): %s", " ".join(args))
    if bl.args.bootstrap:
        bootstrap_load()
    elif bl.args.notes:
        notes_load()
    elif bl.args.mbsystem:
        mbsystem_load()
    else:
        bootstrap_load()
        notes_load()
        mbsystem_load()


def bootstrap_load():
    sc = Scanner()
    sc.process_command_line()

    if sc.args.clobber:
        # Will cascade delete Missions and Notes loaded by bootstrap load
        if not sc.args.noinput:
            ans = input(
                "\nAre you sure you want to delete all existing Expeditions? [y/N] "
            )
            if ans.lower() == "y":
                sc.logger.info(
                    "Deleting %s Expeditions", Expedition.objects.all().count()
                )
                for expd in Expedition.objects.all():
                    expd.delete()

    # Avoid ._ZTopo.grd and ZTopo.grd.cmd files with regex locate
    locate_cmd = f"locate -d {sc.LOCATE_DB} -r '\/ZTopo.grd$'"
    start_processing = True
    if sc.args.skipuntil_regex:
        start_processing = False
    miss_count = 0
    for count, fp in enumerate(subprocess.getoutput(locate_cmd).split("\n")):
        sc.logger.debug("%3d. file: %s", count, fp)
        if sc.args.regex:
            if sc.args.skipuntil_regex and re.search(re.compile(sc.args.regex), fp):
                start_processing = True
            if not sc.args.skipuntil_regex and not re.search(
                re.compile(sc.args.regex), fp
            ):
                sc.logger.debug("Does not match --regex '%s'", sc.args.regex)
                continue
        if not start_processing:
            sc.logger.debug("Waiting for %s to start processing", sc.args.regex)
            continue
        if fp in sc.exclude_files:
            sc.logger.debug("Excluding file: %s", fp)
        else:
            try:
                ds = Dataset(fp)
                sc.logger.debug(ds)
            except PermissionError as e:
                sc.logger.warning(str(e))
            except FileNotFoundError:
                raise FileNotFoundError(f"Could not open {fp}\nIs {MBARI_DIR} mounted?")
            if not sc.is_geographic(ds):
                sc.logger.warning("%s is not Projection: Geographic", fp)
                continue
            try:
                grid_bounds = sc.extent(ds, fp)
            except ValueError as e:
                sc.logger.warning(e)
                continue
            sc.logger.debug("grid_bounds: %s", grid_bounds)

            notes_filename = sc.notes_filename(os.path.dirname(fp))
            thumbnail_filename = sc.thumbnail_filename(os.path.dirname(fp))

            expedition, _ = Expedition.objects.get_or_create(
                expd_path_name=os.path.dirname(fp)
            )
            mission, created = Mission.objects.get_or_create(
                name=os.path.dirname(fp).replace(MBARI_DIR, ""),
                expedition=expedition,
                grid_bounds=grid_bounds,
                notes_filename=notes_filename,
                thumbnail_filename=thumbnail_filename,
            )
            try:
                sc.save_notes(mission)
                sc.save_thumbnail(mission)
            except FileExistsError as e:
                sc.logger.warning(str(e))

            miss_count += 1
            if created:
                sc.logger.info("%3d. Saved %s", miss_count, mission)
            else:
                sc.logger.info("%3d. Resaved %s", miss_count, mission)
            if sc.args.limit:
                if miss_count >= sc.args.limit:
                    sc.logger.info("Stopping after %s records", sc.args.limit)
                    return


def notes_load():
    np = NoteParser()
    np.process_command_line()
    np.parse_texts()
    np.save_expd_name_from_comment()


def mbsystem_load():
    mbs = MBSystem()
    mbs.process_command_line()
    mbs.process_missions()


if __name__ == "__main__":
    run()
