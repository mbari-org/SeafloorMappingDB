#!/usr/bin/python
"""
Load data from SeafloorMapping share into a postgis database
"""

from distutils import cmd
import os
import sys
from typing import Iterator, List, Tuple

import django

parentDir = os.path.join(os.path.dirname(__file__), "../")
sys.path.insert(0, parentDir)
os.environ["DJANGO_SETTINGS_MODULE"] = f"config.settings.{os.environ['BUILD_ENV']}"
django.setup()

import argparse  # noqa F402
import getpass  # noqa F402
import logging  # noqa F402
import math  # noqa F402
import pandas as pd  # noqa F402
import pathlib  # noqa F402
import re  # noqa F402
import subprocess  # noqa F402
import tempfile  # noqa F402
from netCDF4 import Dataset  # noqa F402
from datetime import date, datetime, timedelta  # noqa F402
from dateutil.parser import ParserError, parse  # noqa F402
from django.conf import settings  # noqa F402
from django.core.files import File  # noqa F402
from django.core.files.base import ContentFile  # noqa F402
from django.core.files.storage import DefaultStorage  # noqa F402
from django.contrib.gis.geos import Point, Polygon, LineString  # noqa F402
from glob import glob
from PIL import Image, UnidentifiedImageError  # noqa F402
from smdb.models import (
    Compilation,
    Expedition,
    Mission,
    Platform,
    Platformtype,
    Quality_Category,
)  # noqa F402
from subprocess import check_output, TimeoutExpired  # noqa F402
from time import time  # noqa F402

MBARI_DIR = "/mbari/SeafloorMapping/"

instructions = f"""
Loading a Seafloor Mapping Database is at least a three step process, with
some steps requiring access to the SeafloorMapping share on titan. They are:

1. --bootstrap          Requires SeafloorMapping access
2. --notes
3. --fnv                Requires SeafloorMapping access
4. --compilation        Requires SeafloorMapping access
5. --spreadsheets       Requires SeafloorMapping access

With none of these options specified all are executed. Specify one or more
of these options to debug portions of code or to pick up where a previous
load may have failed. The --skipuntil option may be used to skip over missions
that have already been loaded. (See the .vscode/launch.json file for various
options that have proved useful.)

A locate(1) database is used to speed lookups of files from the SeafloorMapping
share. Make sure you have an up to date copy on your development system, e.g.:

  cd ~/
  scp smdb.shore.mbari.org:/opt/docker_smdb_vol/SeafloorMapping.db docker_smdb_vol

Can be run from smdb Docker environment thusly...
    From VS Code:
        - Mount smb://titan.shore.mbari.org/SeafloorMapping
        - Open zsh terminal, cd to /app/smdb, at ➜  smdb git:(main) prompt:
          scripts/load.py --help
          scripts/load.py -v --clobber
          or use the "load.py" Run and Debug launch configuration
    On production server:
        - From account with permissions in /opt/SeafloorMappingDB:
          export SMDB_HOME=$(pwd)
          export COMPOSE_FILE=$SMDB_HOME/smdb/production.yml
          docker-compose run --rm  django scripts/load.py -v --clobber | tee load.out
        - It's useful to capture the output and use the WARNING statements to fix problems

"""


class BaseLoader:
    LOG_FILE = "load.txt"
    LOCAL_LOG_FILE = f"/etc/smdb/{LOG_FILE}"
    MEDIA_LOG_FILE = f"logs/{LOG_FILE}"
    MEDIA_EXCLUDE_LIST_FILE = "logs/exclude_list.txt"
    LOCATE_DB = "/etc/smdb/SeafloorMapping.db"

    def __init__(self):
        self.logger = logging.getLogger("load")
        self._log_levels = (logging.WARN, logging.INFO, logging.DEBUG)
        self._log_strings = ("WARN", "INFO", "DEBUG")
        self.commandline = None
        self.exclude_paths = set()
        self.start_proc = datetime.now()

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
            help="Name of file containing Mission paths to exclude",
            default=os.path.join(settings.ROOT_DIR, "config/exclude.list"),
        )
        parser.add_argument(
            "--regex",
            action="store",
            help="Load only ZTopo.grd files that have this regular expression in their path",
            default=".*",
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
            "--mbinfo",
            action="store_true",
            help="Deprecated in favor of --fnv. Run the loading steps that uses MB-System mbinfo commands",
        )
        parser.add_argument(
            "--fnv",
            action="store_true",
            help="Run the loading steps that parse .fnv files for nav_track and other data",
        )
        parser.add_argument(
            "--compilation",
            action="store_true",
            help="Finds directories with datalist*.mb-1, but without ZTopo.grd files, indicating a Compilation",
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
            help="Don't ask to confirm when --clobber is specified",
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
        parser.add_argument(
            "--log_file",
            action="store",
            help=f"Override log file name {self.LOG_FILE}",
        )
        parser.add_argument(
            "--filter",
            action="store",
            help="Process only Compilation directories that match this text",
        )
        parser.add_argument(
            "--no_compilation_thumbnails",
            action="store_true",
            help="Do not process and save thumbnails for Compilations - for speeding up the process",
        )
        parser.add_argument(
            "--spreadsheets",
            action="store_true",
            help="Load data from .xlss spreadsheets and write out parallel .csv files",
        )
        parser.add_argument(
            "--last_n_days",
            action="store",
            type=float,
            help="For each locate(1) command look back this number of days for files (may be fractional)",
        )
        parser.add_argument(
            "--parent_dir",
            action="store",
            help=f"Read or write a .xlsx or .csv file for the direct sub-directory of {MBARI_DIR}",
        )
        parser.add_argument(
            "--clobber_log_file",
            action="store_true",
            help="Remove existing log file and start a new one",
        )

        self.args = parser.parse_args()  # noqa
        self.commandline = " ".join(sys.argv)

        # Override Django's logging so that we can setLevel() with --verbose
        logging.getLogger().handlers.clear()
        _formatter = logging.Formatter(
            "%(levelname)s %(asctime)s %(filename)s "
            "%(funcName)s():%(lineno)d %(message)s"
        )
        if self.args.log_file:
            self.LOCAL_LOG_FILE = f"/etc/smdb/{self.args.log_file}"
            self.MEDIA_LOG_FILE = f"logs/{self.args.log_file}"
        if not self.logger.handlers:
            # Don't add handlers when sub class runs
            stream_handler = logging.StreamHandler()
            if os.path.exists(self.LOCAL_LOG_FILE) and self.args.clobber_log_file:
                os.remove(self.LOCAL_LOG_FILE)
            file_handler = logging.FileHandler(self.LOCAL_LOG_FILE)
            stream_handler.setFormatter(_formatter)
            file_handler.setFormatter(_formatter)
            self.logger.addHandler(stream_handler)
            self.logger.addHandler(file_handler)
        self.logger.setLevel(self._log_levels[self.args.verbose])

        if self.args.clobber_log_file:
            self.logger.info("Saving to new local log file: %s", self.LOCAL_LOG_FILE)
        else:
            self.logger.debug("Appending to local log file: %s", self.LOCAL_LOG_FILE)
        self.logger.debug(
            "Using database at DATABASE_URL = %s", os.environ["DATABASE_URL"]
        )

    def update_missions(self, method_to_run: str, missions_saved: list) -> None:
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
            if self.args.last_n_days:
                if mission not in missions_saved:
                    self.logger.debug("Skipping %s", mission.name)
                    continue
            try:
                self.logger.info("======= %d. %s ========", miss_count, mission)
                # The passed method_to_run can be anything that updates
                # the fields of a mission object.  Initial ones include:
                #   self.mbinfo_update_mission_data(mission)
                #   self.fnv_update_mission_data(mission)
                getattr(self, method_to_run)(mission)
            except (ParserError, FileNotFoundError) as e:
                self.logger.warning(e)
            if self.args.limit:
                if miss_count >= self.args.limit:
                    return

    def save_logger_output(self) -> None:
        self.logger.info("Elapsed time: %s", datetime.now() - self.start_proc)
        for handler in self.logger.handlers[:]:
            self.logger.debug("Closing handler: %s", handler)
            handler.close()
            self.logger.removeHandler(handler)
        with open(self.LOCAL_LOG_FILE) as log_file:
            ds = DefaultStorage()
            ds.delete(self.MEDIA_LOG_FILE)
            self.logger.info(
                "Copying local log file to media log file: %s", self.MEDIA_LOG_FILE
            )
            ds.save(self.MEDIA_LOG_FILE, ContentFile(log_file.read().encode()))

    def extent(self, ds, file):
        if "x" in ds.variables and "y" in ds.variables:
            X = "x"
            Y = "y"
        elif "lon" in ds.variables and "lat" in ds.variables:
            X = "lon"
            Y = "lat"
        else:
            raise ValueError(f"Did not find x/y nor lon/lat in file {file}")
        if (
            ds[X].long_name.lower() != "longitude"
            or ds[Y].long_name.lower() != "latitude"
        ):
            raise ValueError(
                f"Expected Longitude/Latitude but found {ds[X].long_name}/{ds[Y].long_name}"
            )
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

    def save_thumbnail(self, mission, scale_factor=8):
        # Factored out of BootStrapper() to be used also by Compiler()
        # (mission may also be a compilation object)
        # https://stackoverflow.com/a/51152514/1281657
        Image.MAX_IMAGE_PIXELS = 933120000
        if not mission.thumbnail_filename:
            raise FileExistsError(f"No thumbnail image found for {mission}")
        try:
            with Image.open(mission.thumbnail_filename) as im:
                width, height = im.size
                nx = width // scale_factor
                ny = height // scale_factor
                self.logger.info(
                    "Resizing image %s to %dx%d", mission.thumbnail_filename, nx, ny
                )
                new_im = im.resize((nx, ny))
        except (
            UnidentifiedImageError,
            FileNotFoundError,
            OSError,
            Image.DecompressionBombError,
        ) as e:
            self.logger.warning(f"{e}")
            return

        new_name = "_".join(
            mission.thumbnail_filename.replace(MBARI_DIR, "").split("/")
        )
        with tempfile.TemporaryDirectory() as thumbdir:
            im_path = os.path.join(thumbdir, new_name)
            if im_path.endswith(".jpg"):
                new_im.save(im_path, "JPEG")
            if im_path.endswith(".png"):
                new_im.save(im_path, "PNG")
            if im_path.endswith(".tif"):
                new_name = new_name.replace(".tif", ".png")
                new_im.save(im_path, "PNG")
            with open(im_path, "rb") as fh:
                # Original file will not be overwritten, delete first
                mission.thumbnail_image.delete()
                mission.thumbnail_image.save(new_name, File(fh))
                self.logger.debug(
                    "thumbnail_image.url: %s", mission.thumbnail_image.url
                )
                self.logger.info("Saved thumbnail image of size %dx%s", nx, ny)


class NoteParser(BaseLoader):
    BOUNDARY_DASHES = "------------------------------------"

    def comment_from_text(self, mission: Mission) -> str:
        comment_captured = False
        comment = ""
        if not mission.notes_text:
            return comment
        for line in mission.notes_text.split("\n"):
            if not comment_captured:
                self.logger.debug(line)
                # Capture lines starting at the first line
                comment += line + "\n"
            if line == self.BOUNDARY_DASHES and not comment_captured:
                comment_captured = True
                comment = comment.replace(self.BOUNDARY_DASHES, "").strip()
                if mission.comment == "":
                    self.logger.warning("Empty comment for mission %s", mission)
            if line.strip() in (
                "TN199 Expedition to the Juan de Fuca Ridge",
                "2007 PMEL Nemo Expedition (AT15-21)",
                "Science Party: Dave Caress, Hans Thomas, Rendi Keaton",
            ):
                # /mbari/SeafloorMapping/MappingAUVOps2016/20160919OCEANSTutorial/SampleDatasets/20060901Org/20060831Notes.txt
                # /mbari/SeafloorMapping/MappingAUVOps2016/20160919OCEANSTutorial/SampleDatasets/20070808/20070808Notes.txt
                # /mbari/SeafloorMapping/MappingAUVOpsStuff/2005/ZZoldstuff/20051118/Notes.txt
                # Special cases where the Notes file has no BOUNDARY_DASHES
                comment_captured = True

        return comment

    def expd_db_id_from_text(self, mission: Mission) -> int:
        next_line_is_expd_db_id = False
        expd_db_id = None
        if not mission.notes_text:
            return expd_db_id
        for line in mission.notes_text.split("\n"):
            if next_line_is_expd_db_id:
                try:
                    expd_db_id = int(line)
                except ValueError:
                    self.logger.warning(
                        "Could not get expd_db_id for %s from Notes file %s",
                        mission.name,
                        mission.notes_filename,
                    )
                next_line_is_expd_db_id = False
            if "ExpeditionID" in line:
                self.logger.debug(line)
                if expd_ma := re.match(r"ExpeditionID\s+(\d+)", line):
                    # ExpeditionID	6229
                    expd_db_id = int(expd_ma.group(1))
                    next_line_is_expd_db_id = False
                else:
                    next_line_is_expd_db_id = True
        return expd_db_id

    def expedition_name_from_comment(self, mission: Mission) -> str:
        # Take the third and following lines (count > 1) from the comment
        expd_name = ""
        if not mission.comment:
            self.logger.warning("Empty comment for mission %s", mission)
            if mission.notes_text:
                self.logger.debug("misison.notes_text = \n%s", mission.notes_text)
            return expd_name.strip()
        for count, line in enumerate(mission.comment.split("\n")):
            if count > 1:
                expd_name += line + " "
        return expd_name.strip()

    def platform_from_comment(self, mission: Mission) -> str:
        standard_platform_names = (
            "Icebreaker Araon",
            "R/V Falkor",
            "R/V Kilo Moana",
            "R/V Rachel Carson",
            "R/V Western Flyer",
            "R/V Zephyr",
        )
        # It looks like the third line has the Platform (ship) name
        # Pull out just the ship name using standard_platform_names
        if not mission.comment:
            return None
        platform_name = ""
        maybe_platform_name = mission.comment.split("\n")[2]
        if "Zephyr" in maybe_platform_name:
            self.logger.info(maybe_platform_name)
        for standard_platform_name in standard_platform_names:
            if standard_platform_name in maybe_platform_name:
                platform_name = standard_platform_name
                break
        if not platform_name:
            platform_name = maybe_platform_name

        if platform_name in (
            "R/V Rachel Carson",
            "R/V Western Flyer",
            "R/V Zephyr",
        ):
            operator_org_name = "MBARI"
        else:
            # TODO: Make additional assignments
            operator_org_name = ""
        platformtype, _ = Platformtype.objects.get_or_create(name="ship")
        platform, _ = Platform.objects.get_or_create(
            name=platform_name,
            platformtype=platformtype,
            operator_org_name=operator_org_name,
        )
        return platform

    def route_file_from_text(self, mission: Mission) -> str:
        # Return .rte file name from notes_text that looks like:
        # Mission Summary:
        #     Route File:               MC_2150_m1_v2.rte
        if not mission.notes_text:
            return None
        for line in mission.notes_text.split("\n"):
            if "Route File:" in line:
                return line.split(":")[1].strip()

    def parse_notes(self, missions_saved: list) -> None:
        for note_count, mission in enumerate(Mission.objects.all(), start=1):
            if self.args.last_n_days:
                if mission not in missions_saved:
                    self.logger.debug(
                        "Skipping %s as it's not in the missions_saved list",
                        mission.name,
                    )
                    continue
            self.logger.info("======== %d. %s ========", note_count, mission.name)
            mission.comment = self.comment_from_text(mission)
            if len(mission.comment) > 512:
                self.logger.warning(
                    "Comment parsed from notes_text %s is too long at %d characters",
                    mission.notes_filename,
                    len(mission.comment),
                )
                self.logger.info("Truncating it to first 5 lines")
                mission.comment = "\n".join(mission.comment.split("\n")[:5])
            # Append Expedition Database expd_id to name parsed from notes
            # to ensure unique names. TODO: consider using a m2m table for this.
            expd_db_id = self.expd_db_id_from_text(mission)
            name = f"{self.expedition_name_from_comment(mission)}"
            if len(name) > 200:
                self.logger.warning(
                    "Truncating 4th line (Expedition name) from %d characters to 200",
                    len(name),
                )
                name = name[:200]
            if expd_db_id:
                name += f" - {expd_db_id}"
            expedition, created = Expedition.objects.get_or_create(
                expd_db_id=expd_db_id, name=name
            )
            if created:
                self.logger.info("Saved <Expedition: %s>", expedition)
            else:
                self.logger.info("Reusing <Expedition: %s>", expedition)
                self.logger.info(
                    "Other missions belonging to %s: %s",
                    expedition,
                    ", ".join(
                        Mission.objects.filter(expedition=expedition)
                        .exclude(pk=mission.pk)
                        .values_list("name", flat=True)
                    ),
                )
            mission.expedition = expedition
            mission.platform = self.platform_from_comment(mission)
            mission.route_file = self.route_file_from_text(mission)
            mission.save()
            self.logger.info(
                "%3d. Saved Mission with <Platform: %s>",
                note_count,
                mission.platform,
            )


class FNVLoader(BaseLoader):
    def fnv_file_list(self, path: str, datalist: str) -> Tuple[list, str]:
        fnv_list = []
        fnv_type = ""
        with open(datalist) as fh:
            for line in fh.readlines():
                if not line.strip():
                    continue
                if line.startswith("#"):
                    continue
                item = line.split()[0].strip()
                if item.endswith("mb-1"):
                    return self.fnv_file_list(
                        path,
                        os.path.join(path, item),
                    )
                elif ma := re.match(r"(.+)(\.mb\d\d)", item):
                    # Prefer processed '*p.mb8[8-9]' files
                    fnv_type = "processed"
                    fnv_file = os.path.join(
                        path,
                        ma.group(1) + "p" + ma.group(2) + ".fnv",
                    )
                    if not os.path.exists(fnv_file):
                        fnv_type = "unprocessed"
                        fnv_file = os.path.join(path, item + ".fnv")
                    fnv_list.append(fnv_file)
        return fnv_list, fnv_type

    def fnv_start_and_end_data(
        self, fnv_list: list
    ) -> Tuple[datetime, datetime, float, float, Point, Point]:
        # Expect that fnv_list files are ordered in time
        # Assume mblist(1) output options of -OtMXYHSc
        # 11. c for sonar tranducer depth (m)
        for fnv_file in fnv_list:
            with open(fnv_file) as fh:
                try:
                    for line in fh.readlines():
                        # Get first non-comment line
                        if not line.startswith("#"):
                            break
                except IndexError:
                    self.logger.debug("Cannot read first record from %s", fnv_file)
                    continue
                try:
                    start_dt = parse("{}-{}-{} {}:{}:{}".format(*line.split()[:6]))
                except NameError:
                    self.logger.debug("No line read from file %s", fnv_file)
                    continue
                lon = float(line.split()[7])
                lat = float(line.split()[8])
                start_point = Point((lon, lat), srid=4326)
                start_depth = float(line.split()[11])
            break
        if "start_dt" not in locals():
            raise ParserError(f"Could not get start_dt from {fh.name}")
        for fnv_file in reversed(fnv_list):
            with open(fnv_file) as fh:
                try:
                    # Assume no comments at end of file
                    line = fh.readlines()[-1]
                except IndexError:
                    self.logger.debug("Cannot read last record from %s", fnv_file)
                    continue
                try:
                    end_dt = parse("{}-{}-{} {}:{}:{}".format(*line.split()[:6]))
                except IndexError:
                    self.logger.debug("Failed to parse datetime from %s", line)
                    continue
                try:
                    lon = float(line.split()[7])
                    lat = float(line.split()[8])
                except IndexError:
                    self.logger.debug("Failed to parse lon or lat from %s", line)
                    continue
                end_point = Point((lon, lat), srid=4326)
                end_depth = float(line.split()[11])
            break
        if "end_dt" not in locals():
            raise ParserError(f"Could not get end_dt from {fh.name}")

        return start_dt, end_dt, start_depth, end_depth, start_point, end_point

    def fnv_determine_subsample(
        self,
        fnv_file: str,
        interval: timedelta,
    ) -> int:
        # Read records to determine number of records to subsample
        # Return after getting 2 successive identical intervals
        last_subsample = 0
        interval_count = 0
        line_count = 0
        with open(fnv_file) as fh:
            for line in fh.readlines():
                if line.startswith("#"):
                    continue
                line_count += 1
                interval_count += 1
                try:
                    dt = parse("{}-{}-{} {}:{}:{}".format(*line.split()[:6]))
                except ParserError as e:
                    raise ParserError(
                        f"Could not parse datetime from line number {line_count} in file {fnv_file}"
                    )
                if "last_dt" not in locals():
                    last_dt = dt
                if dt - last_dt > interval:
                    subsample = interval_count
                    if subsample == last_subsample:
                        return subsample
                    last_dt = dt
                    last_subsample = subsample
                    interval_count = 0
        if line_count:
            raise EOFError(
                "{} has {} records lasting {} - shorter than interval {}".format(
                    fnv_file,
                    line_count,
                    dt - last_dt,
                    interval,
                ),
            )
        else:
            raise EOFError(f"{fnv_file} is empty")

    def haversine(self, lon1: float, lat1: float, lon2: float, lat2: float) -> float:
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        https://gis.stackexchange.com/a/56589/62207
        """
        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))
        km = 6367 * c
        return km

    def linestring_length(self, linestring: LineString) -> float:
        dist = 0
        self.logger.debug(
            "Computing linestring length for %s points",
            len(linestring),
        )
        for i in range(len(linestring.coords) - 1):
            dist += self.haversine(
                linestring.coords[i][0],
                linestring.coords[i][1],
                linestring.coords[i + 1][0],
                linestring.coords[i + 1][1],
            )
        self.logger.debug("Total distance: %f km", dist)
        return dist

    def fnv_points_tolinestring(
        self,
        fnv_list: list,
        interval: timedelta = timedelta(seconds=30),
        tolerance: float = 0.00001,
    ) -> Tuple[int, LineString, float]:
        """Can tune the quality of simplified LineString by adjusting
        `interval` and `tolerance`. Reasonable defaults are provided
        for quick rendering of maybe 600 Missions on a Leaflet map."""
        point_list = []
        for fnv_file in fnv_list:
            try:
                subsample = self.fnv_determine_subsample(fnv_file, interval)
                break
            except EOFError as e:
                self.logger.debug(e)
        if "subsample" not in locals():
            self.logger.info("Not getting nav_track for this mission.")
            return len(point_list), None, None
        line_count = 0
        for fnv in fnv_list:
            try:
                with open(fnv) as fh:
                    for line_count, line in enumerate(fh.readlines(), start=1):
                        if line_count % subsample:
                            continue
                        # 2019 01 24 18 12 32.236999      1548353552.236999       -121.9451060788   36.6959160254  65.819  4.354  48.2750 -4.032   2.946   0.0000 -121.9455617494   36.6968155796 -121.9445069464   36.6949795110
                        lon = float(line.split()[7])
                        lat = float(line.split()[8])
                        point_list.append(Point((lon, lat), srid=4326))
            except UnicodeDecodeError:
                self.logger.debug("UnicodeDecodeError with file %s", fnv)
                continue
            except OSError as e:
                # Likely OSError: [Errno 24] Too many open files
                self.logger.error(e)
                continue
            if line_count:
                self.logger.debug(
                    "Collected %d points every %s from %s",
                    line_count,
                    interval,
                    fnv,
                )
        self.logger.debug(
            "%d points collected from %d .fnv files",
            len(point_list),
            len(fnv_list),
        )
        nav_track = LineString(point_list, srid=4326).simplify(tolerance=tolerance)
        self.logger.debug(
            "Simplified %d points from %d files to %d points with tolerance = %f",
            len(point_list),
            len(fnv_list),
            len(nav_track),
            tolerance,
        )
        # linestring_length() uses haversine() and is slow
        ##track_length = round(self.linestring_length(nav_track), 4)
        ##self.logger.info("track_length = %.4f km", track_length)
        # Pulling values from .inf files is much faster
        dist_sum = 0
        self.logger.info(f"Computing total distance from {len(fnv_list)} .inf files")
        for fnv in fnv_list:
            inf_file = fnv.replace(".fnv", ".inf")
            try:
                with open(inf_file) as fh:
                    for line in fh.readlines():
                        # Total Track Length:     0.6137 km
                        if line.startswith("Total Track Length:"):
                            dist_sum += float(line.split()[-2])
                            break
            except OSError as e:
                # Likely OSError: [Errno 24] Too many open files
                self.logger.error(e)
                self.logger.info("dist_sum = %.4f km so far", dist_sum)
                continue
        self.logger.info("dist_sum = %.4f km", dist_sum)
        ##if dist_sum != 0:
        ##    self.logger.info(
        ##        "track_length / dist_sum = %.2f%%", 100 * track_length / dist_sum
        ##    )
        return len(point_list), nav_track, dist_sum

    def fnv_update_mission_data(self, mission: Mission):
        # Start with datalistp.mb-1 and recurse down
        # to find list of .fnv files.  Construct data
        # for Mission fields.
        path = mission.directory
        datalist = os.path.join(path, "datalistp.mb-1")
        fnv_list, fnv_type = self.fnv_file_list(path, datalist)
        if not fnv_list:
            raise FileNotFoundError(f"No .fnv files found in {path}")
        if path.endswith("lidar") or path.endswith("lidartest"):
            (
                original,
                mission.nav_track,
                mission.track_length,
            ) = self.fnv_points_tolinestring(
                fnv_list,
                interval=timedelta(seconds=5),
            )
        else:
            (
                original,
                mission.nav_track,
                mission.track_length,
            ) = self.fnv_points_tolinestring(fnv_list)
        (
            mission.start_date,
            mission.end_date,
            mission.start_depth,
            _,  # mission.end_depth,
            mission.start_point,
            _,  # mission.end_point,
        ) = self.fnv_start_and_end_data(fnv_list)
        mission.save()
        self.logger.info(
            "Saved start & end: %s to %s", mission.start_date, mission.end_date
        )
        self.logger.info(
            "Saved start_point & start_depth: %s & %s meters",
            mission.start_point,
            mission.start_depth,
        )
        if mission.nav_track:
            self.logger.info(
                "Saved nav_track: %d points (originally %d) from %d %s files",
                len(mission.nav_track),
                original,
                len(fnv_list),
                fnv_type,
            )


class MBSystem(BaseLoader):
    SSH_CMD = f"ssh {getpass.getuser()}@mb-system"
    TIMEOUT = 360  # Max seconds to retrieve file from tertiary storage

    def sonar_start_data(self, sonar_file: str) -> Tuple[datetime, Point, float]:
        cmd = f"{self.SSH_CMD} mbinfo -I {sonar_file}"
        start_line = False

        self.logger.debug("Executing %s", cmd)
        try:
            start_esec = time()
            lines = check_output(cmd.split(), timeout=self.TIMEOUT).decode().split("\n")
        except TimeoutExpired:
            self.logger.warning("Timeout for: %s", cmd)
            raise TimeoutExpired(cmd, self.TIMEOUT)
        ma_pd = None
        for line in lines:
            if start_line:
                if line.startswith("Time"):
                    # Time:  03 18 2019 12:09:53.564998  JD77 (2019-03-18T12:09:53.564998)
                    ma_ti = re.match(
                        r"Time:.+\((\d\d\d\d\-\d\d-\d\dT\d\d:\d\d:\d\d\.\d+)\)",
                        line,
                    )
                if line.startswith("Lon"):
                    # Lon:  -121.945106079     Lat:    36.695916025     Depth:    48.2750 meters
                    ma_pd = re.match(
                        r"Lon:\s+(-?[0-9.]*)\s+Lat:\s+(-?[0-9.]*)\s+Depth:\s+(-?[0-9.]*)",
                        line,
                    )
                    point = Point(
                        (float(ma_pd.group(1)), float(ma_pd.group(2))), srid=4326
                    )
                if ma_ti and ma_pd:
                    self.logger.debug(
                        "%4.2f seconds to scan %s", time() - start_esec, sonar_file
                    )
                    return parse(ma_ti.group(1)), point, float(ma_pd.group(3))
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

    def first_sonar_data(
        self, path: str, datalist: str
    ) -> Tuple[datetime, Point, float]:
        with open(datalist) as fh:
            for line in fh.readlines():
                if line.startswith("#"):
                    continue
                item = line.split()[0].strip()
                if item.endswith("mb-1"):
                    return self.first_sonar_data(path, os.path.join(path, item))
                elif re.match(r".+\.mb\d\d", item):
                    return self.sonar_start_data(os.path.join(path, item))

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

    def mbinfo_update_mission_data(self, mission: Mission):
        # Start with datalistp.mb-1 and recurse down
        # to find first and last sonar file and corresponding
        # first and last data values for the mission
        path = mission.directory
        datalist = os.path.join(path, "datalistp.mb-1")
        (
            mission.start_date,
            mission.start_point,
            mission.start_depth,
        ) = self.first_sonar_data(path, datalist)
        mission.end_date = self.last_sonar_time(path, datalist)
        mission.save()
        self.logger.info(
            "Saved start & end: %s to %s", mission.start_date, mission.end_date
        )
        self.logger.info(
            "Saved start_point & start_depth: %s & %s meters",
            mission.start_point,
            mission.start_depth,
        )


class BootStrapper(BaseLoader):
    missions_saved = []

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

    def valid_notes_filename(self, txt_file):
        if "junk" in txt_file:
            self.logger.debug("Directory contains'junk': %s", txt_file)
            return False
        if self._exclude_path(txt_file):
            self.logger.debug("Directory in exclude.list: %s", txt_file)
            return False
        try:
            if os.stat(txt_file).st_size == 0:
                self.logger.debug("Empty notes file: %s", txt_file)
                return False
        except FileNotFoundError:
            self.logger.debug("Note file not found: %s", txt_file)
            return False
        return True

    def notes_filename(self, sm_dir):
        locate_cmd = f"locate -d {self.LOCATE_DB} -r '{sm_dir}.*Notes.txt$'"
        notes_file = None
        with subprocess.Popen(locate_cmd, shell=True, stdout=subprocess.PIPE) as proc:
            for txt_file in proc.stdout:
                txt_file = txt_file.decode().strip()
                if self.valid_notes_filename(txt_file):
                    self.logger.info("Potential notes file: %s", txt_file)
                    notes_file = txt_file

        if not notes_file:
            # Try parent directory
            parent_dir = os.path.abspath(os.path.join(sm_dir, ".."))
            for txt_file in glob(f"{parent_dir}/*Notes.txt"):
                if self.args.last_n_days:
                    if os.path.getmtime(txt_file) < self.args.last_n_days:
                        self.logger.debug(
                            f"Skipping notes file older than {self.args.last_n_days = }: {txt_file}"
                        )
                        continue
                if self.valid_notes_filename(txt_file):
                    self.logger.info("Potential notes file: %s", txt_file)
                    notes_file = txt_file
        if not notes_file:
            # Try grandparent directory
            grandparent_dir = os.path.abspath(os.path.join(sm_dir, "../.."))
            for txt_file in glob(f"{grandparent_dir}/*Notes.txt"):
                if self.valid_notes_filename(txt_file):
                    self.logger.info("Potential notes file: %s", txt_file)
                    notes_file = txt_file
        if not notes_file:
            # Try greatgrandparent directory
            greatgrandparent_dir = os.path.abspath(os.path.join(sm_dir, "../../.."))
            for txt_file in glob(f"{greatgrandparent_dir}/*Notes.txt"):
                if self.valid_notes_filename(txt_file):
                    self.logger.info("Potential notes file: %s", txt_file)
                    notes_file = txt_file
        return notes_file

    def thumbnail_filename(self, sm_dir: str) -> str:
        locate_base = f"locate -d {self.LOCATE_DB} -r '{sm_dir}"
        locate_cmd = f"{locate_base}/ZTopoSlopeNav.jpg'"
        thumbnail_file = ""
        with subprocess.Popen(locate_cmd, shell=True, stdout=subprocess.PIPE) as proc:
            for jpg_file in proc.stdout:
                jpg_file = jpg_file.decode().strip()
                self.logger.debug("Potential jpg thumbnail file: %s", jpg_file)
                thumbnail_file = jpg_file
        if not thumbnail_file:
            locate_cmd = f"{locate_base}/ZTopoSlopeNav.png'"
            with subprocess.Popen(
                locate_cmd, shell=True, stdout=subprocess.PIPE
            ) as proc:
                for png_file in proc.stdout:
                    png_file = png_file.decode().strip()
                    self.logger.debug("Potential png thumbnail file: %s", png_file)
                    thumbnail_file = png_file

        return thumbnail_file

    def save_note_todb(self, mission):
        if not mission.notes_filename:
            raise FileExistsError(f"No Notes found for {mission}")
        note_text = ""
        with open(mission.notes_filename, errors="ignore") as fh:
            for line_count, line in enumerate(fh.readlines()):
                # Blank out potentially sensitive information
                if ma := re.match(r"\s+password:\s*(.*)", line, re.IGNORECASE):
                    line = line.replace(ma.group(1), "*********")
                if re.search(r"\d+\.\d+\.\d+\.\d+", line):
                    # Remove everything after the IP address
                    line = re.sub(
                        r"\d+\.\d+\.\d+\.\d+.+",
                        "***.***.***.***",
                        line,
                    )
                if ma := re.match(r"\s+User:\s*(.*)", line, re.IGNORECASE):
                    line = line.replace(ma.group(1), "*********")
                note_text += line

        if not note_text:
            raise FileExistsError(f"No Notes found for {mission}")

        mission.notes_text = note_text
        mission.save()
        self.logger.info(f"Saved note text: %d lines", line_count)

    def flush_database(self):
        """Delete all records without resetting primary keys"""
        self.logger.info("Deleting...")
        self.logger.info("%d stored thumbnail_images", Mission.objects.all().count())
        self.logger.info("%d Missions", Mission.objects.all().count())
        for mission in Mission.objects.all():
            mission.thumbnail_image.delete(save=False)
        self.logger.info("%d Expeditions", Expedition.objects.all().count())
        for expd in Expedition.objects.all():
            expd.delete()
        self.logger.info("%d Platformtypes", Platformtype.objects.all().count())
        for pt in Platformtype.objects.all():
            pt.delete()
        self.logger.info("%d Platforms", Platform.objects.all().count())
        for platform in Platform.objects.all():
            platform.delete()
        self.logger.info("%d Compilations", Compilation.objects.all().count())
        for compilation in Compilation.objects.all():
            compilation.delete()

        # Here's how to automatically flush the whole database resetting pk's:
        # Also removes superuser - Might want to do this at command line:
        # smdb/manage.py flush
        # smdb/manage.py createsuperuser
        ##from django.core.management import call_command  # noqa F402
        ##from django.core.management.commands import flush  # noqa F40
        ##call_command(flush.Command(), verbosity=1, interactive=False)

    def _exclude_path(self, fp):
        for e_path in self.exclude_paths:
            if fp.startswith(e_path):
                self.logger.debug("Excluding file: %s", fp)
                return True
        return False

    def load_from_grds(self):
        self.process_command_line()

        if self.args.clobber:
            # Will cascade delete Missions and Notes loaded by bootstrap load
            if not self.args.noinput:
                ans = input(
                    "\nDelete {} Expeditions and {} Missions? [y/N] ".format(
                        Expedition.objects.all().count(),
                        Mission.objects.all().count(),
                    )
                )
                if ans.lower() == "y":
                    self.flush_database()
            else:
                self.flush_database()
        # Avoid ._ZTopo.grd and ZTopo.grd.cmd files with regex locate
        locate_cmd = f"locate -d {self.LOCATE_DB} -r '\/ZTopo.grd$'"
        start_processing = True
        if self.args.skipuntil_regex:
            start_processing = False
        miss_count = 0
        match_count = 0
        miss_loaded = 0
        exclude_count = 0
        if self.args.last_n_days:
            self.logger.info(
                "Loading Missions newer than %f days", self.args.last_n_days
            )
        with subprocess.Popen(locate_cmd, shell=True, stdout=subprocess.PIPE) as proc:
            for count, fp in enumerate(proc.stdout, start=1):
                fp = fp.decode().strip()
                self.logger.debug("%3d. file: %s", count, fp)
                matches = re.search(re.compile(self.args.regex), fp)
                if matches:
                    match_count += 1
                if self.args.skipuntil_regex and matches:
                    start_processing = True
                if not self.args.skipuntil_regex and not matches:
                    self.logger.debug("Does not match --regex '%s'", self.args.regex)
                    continue
                if not start_processing:
                    self.logger.debug("Skipping until %s", self.args.regex)
                    continue
                if self._exclude_path(fp):
                    exclude_count += 1
                    continue
                if self.args.last_n_days:
                    try:
                        if (
                            os.path.getmtime(fp)
                            < time() - self.args.last_n_days * 86400
                        ):
                            self.logger.debug(
                                f"Skipping file {fp} older than {self.args.last_n_days = }"
                            )
                            continue
                    except FileNotFoundError:
                        # Error seen with smb mount on MacOS but not on Linux
                        self.logger.warning(f"File not found: {fp}")
                        continue
                miss_count += 1
                self.logger.info(
                    "======== %3d. %s ========",
                    miss_count,
                    os.path.dirname(fp).replace(MBARI_DIR, ""),
                )
                try:
                    if not matches.group(4):
                        self.logger.info("Name missing 2 character mission sequence")
                except (AttributeError, IndexError):
                    self.logger.debug("regex match has no group(4)")
                try:
                    ds = Dataset(fp)
                    self.logger.debug(ds)
                except PermissionError as e:
                    self.logger.warning(str(e))
                except FileNotFoundError:
                    raise FileNotFoundError(f"{fp}\nIs {MBARI_DIR} mounted?")
                if not self.is_geographic(ds):
                    self.logger.warning("%s is not Projection: Geographic", fp)
                    continue
                try:
                    grid_bounds = self.extent(ds, fp)
                except ValueError as e:
                    self.logger.warning(e)
                    continue
                self.logger.debug("grid_bounds: %s", grid_bounds)

                notes_filename = self.notes_filename(os.path.dirname(fp))
                thumbnail_filename = self.thumbnail_filename(os.path.dirname(fp))

                mission, created = Mission.objects.get_or_create(
                    name=os.path.dirname(fp).replace(MBARI_DIR, ""),
                    grid_bounds=grid_bounds,
                    notes_filename=notes_filename,
                    thumbnail_filename=thumbnail_filename,
                    directory=os.path.dirname(fp),
                )
                miss_loaded += 1
                try:
                    self.save_note_todb(mission)
                except (FileExistsError, OSError, ValueError) as e:
                    self.logger.warning(str(e))
                try:
                    self.save_thumbnail(mission)
                except (FileExistsError, ValueError) as e:
                    self.logger.warning(str(e))

                if created:
                    self.logger.info("%3d. Saved <Mission: %s>", miss_count, mission)
                    self.missions_saved.append(mission)
                else:
                    self.logger.info("%3d. Resaved %s", miss_count, mission)
                if self.args.limit:
                    if miss_count >= self.args.limit:
                        self.logger.info("Stopping after %s records", self.args.limit)
                        return
        self.logger.info(
            "Count of ZTopo.grd files found with '%s': %d", locate_cmd, count
        )
        self.logger.info(
            "Missions matching regex '%s': %d", self.args.regex, match_count
        )
        self.logger.info("Count of Missions not excluded: %d", miss_count)
        self.logger.info(
            "Count of Missions excluded found in exclude.list file: %d", exclude_count
        )
        self.logger.info("Missions loaded: %d", miss_loaded)


class Compiler(BaseLoader):
    def comp_dirs(self) -> Iterator[str]:
        """Generate potential Compilation directory names, meaning
        there is no ZTopo.grd, but there is a Figure[s]*.cmd file.
        """
        # Pattern needs to end with Figure...cmd with no intervening '/'
        # and must not contain a '.' before Figure
        pattern = r"\/[^\/^\.]*Figure[^\/]*.cmd$"
        locate_cmd = f"locate -d {self.LOCATE_DB} -r '{pattern}'"
        start_processing = True
        if self.args.skipuntil:
            start_processing = False
        with subprocess.Popen(locate_cmd, shell=True, stdout=subprocess.PIPE) as proc:
            for count, fp in enumerate(proc.stdout, start=1):
                fp = fp.decode().strip()
                self.logger.debug("%3d. %s", count, fp)
                # Skip over *Figure*.cmd files that contain 'TEST', 'tmp', 'Copy_of', etc. - ignore case
                if re.search(
                    r"TEST|tmp|temp|Copy_of", fp.split("/")[-1], re.IGNORECASE
                ):
                    self.logger.debug("Skipping %s", fp)
                    continue

                if os.path.exists(f"{os.path.dirname(fp)}/ZTopo.grd"):
                    self.logger.debug("Skipping %s as it is a Mission directory")
                    continue
                if self.args.skipuntil:
                    if self.args.skipuntil in fp:
                        start_processing = True
                if not start_processing:
                    continue
                if self.args.filter:
                    if self.args.filter not in fp:
                        continue
                if self.args.last_n_days:
                    if os.path.getmtime(fp) < time() - self.args.last_n_days * 86400:
                        self.logger.debug(
                            f"Skipping file {fp} older than {self.args.last_n_days = }"
                        )
                        continue
                yield fp

    def mbgrids_from_cmd_to_compilations(
        self, comp_dir: str, cmd_filename: str
    ) -> List[Compilation]:
        """Parse out mbgrid commands from .cmd file"""
        compilations = []
        self.logger.debug(cmd_filename)
        # Find multiple lines like this:
        # mbgrid -I datalist_MAUV_AxialSeamount_2021p.mb-1 \
        #       -R-130.1010316/-129.8350251/45.8289526/46.0569144 \
        #       -A2 -N -F5 -E1/1 -C4 -JU \
        #       -O AxialSummit_2021_Topo1m_UTM
        pattern = re.compile(
            r"""
            mbgrid            # The mbgrid command
            [\s\S]*?          # Zero or more spaces including new lines
            -I\s*(\S+)        # Input file
            [\s\S]*?          # Zero or more spaces including new lines
            -O\s*(\S+)        # Output file
            """,
            re.VERBOSE | re.MULTILINE,
        )
        with open(cmd_filename, errors="ignore") as fd:
            for ma in pattern.finditer(fd.read()):
                grd_filename = os.path.join(comp_dir, ma.group(2)) + ".grd"
                try:
                    grd_file_exists = pathlib.Path(grd_filename).exists()
                    thumbnail_filename = self._thumbnail_filename(
                        os.path.join(comp_dir, ma.group(2))
                    )
                except (PermissionError, FileNotFoundError) as e:
                    self.logger.warning(e)
                    continue
                datalist_filename = os.path.join(comp_dir, ma.group(1))
                if grd_file_exists:
                    mod_time = datetime.fromtimestamp(
                        pathlib.Path(grd_filename).stat().st_mtime
                    )
                    self.logger.info(
                        "%s was created on %s from %s in %s",
                        grd_filename,
                        mod_time,
                        datalist_filename,
                        cmd_filename,
                    )
                    try:
                        grid_bounds = self.extent(
                            Dataset(grd_filename),
                            grd_filename,
                        )
                    except (ValueError, OSError) as e:
                        self.logger.warning(e)
                        grid_bounds = None
                    compilation, _ = Compilation.objects.get_or_create(
                        name=grd_filename.replace(MBARI_DIR, "").replace(".grd", ""),
                        thumbnail_filename=thumbnail_filename,
                        creation_date=mod_time,
                        cmd_filename=cmd_filename,
                        grd_filename=grd_filename,
                        proc_datalist_filename=datalist_filename,
                        grid_bounds=grid_bounds,
                    )
                    compilations.append(compilation)
                else:
                    self.logger.debug(
                        "Referenced from %s %s does not exist",
                        datalist_filename,
                        grd_filename,
                    )
        if compilations:
            self.logger.info(
                "Collected %d Compilations from %s in %s",
                len(compilations),
                datalist_filename,
                cmd_filename,
            )
        return compilations

    def link_compilation_to_missions(self):
        self.logger.info("Linking Compilations to Missions")
        for count, cmd_filename in enumerate(self.comp_dirs()):
            comp_dir = os.path.dirname(cmd_filename)
            self.logger.debug("%4d. %s", count, cmd_filename)
            for compilation in self.mbgrids_from_cmd_to_compilations(
                comp_dir, cmd_filename
            ):
                datalist = str(compilation.grd_filename).replace(".grd", "")
                datalist += ".mb-1"
                mission_names, _ = self.missions_list(comp_dir, datalist)
                mission_ids = []
                if mission_names:
                    self.logger.info(
                        "From %s %s, Potential Missions: %s",
                        datalist,
                        cmd_filename,
                        " ".join(mission_names),
                    )
                    for mission_name in sorted(mission_names):
                        try:
                            mission = Mission.objects.get(name=mission_name)
                            mission_ids.append(mission.id)
                        except Mission.DoesNotExist:
                            self.logger.debug(
                                "Mission not found in database: %s", mission_name
                            )
                if hasattr(compilation, "missions"):
                    self.logger.info(
                        "Linking Mission ids %s to %s",
                        mission_ids,
                        compilation,
                    )
                    for mission_id in mission_ids:
                        compilation.missions.add(Mission.objects.get(pk=mission_id))
                    compilation.save()
                    if not self.args.no_compilation_thumbnails:
                        try:
                            self.save_thumbnail(compilation, scale_factor=16)
                        except (FileExistsError, ValueError, OSError) as e:
                            self.logger.warning(str(e))

    def _thumbnail_filename(self, grd_filename: str) -> str:
        extensions = ("jpg", "jpeg", "png", "tif")
        for ext in extensions:
            base_name = grd_filename.replace(".grd", "")
            thumbnail_filenames = glob(f"{base_name}*.{ext}")
            if len(thumbnail_filenames) == 1:
                return thumbnail_filenames[0]
            elif len(thumbnail_filenames) > 1:
                # Find the most recent one
                last_mod_time = datetime.fromtimestamp(0)
                for thumb in thumbnail_filenames:
                    mod_time = datetime.fromtimestamp(
                        pathlib.Path(thumb).stat().st_mtime
                    )
                    if mod_time > last_mod_time:
                        latest_thumb = thumb
                    last_mod_time = mod_time
                return latest_thumb
        self.logger.info(
            f"Searched {base_name}* and found no files with {extensions = }"
        )

    def _examine_mb1_line(self, path: str, datalist: str, item: str) -> Tuple[
        str,
        str,
    ]:
        if item == os.path.basename(datalist) or (
            datalist.endswith("datalist.mb-1") and item == "datalistp.mb-1"
        ):
            raise RecursionError(
                f"Dangerous recursion detected with '{item}' in {datalist}"
            )
        self.logger.debug("Found '%s' in %s", item, datalist)
        cfile = os.path.abspath(os.path.join(path, item))
        cpath = os.path.dirname(cfile)
        self.logger.debug("Returning path %s and file %s", cpath, cfile)
        return cpath, cfile

    def missions_list(self, path: str, datalist: str) -> Tuple[list, str]:
        """Starting at a datalist file recursively examine each line
        until lines specifying sonar files are found. The paths for those
        files get added to a set that's returned as a list. These are the
        potential Misisons that comprise the Figure/Project/Compilation
        that's defined by the datalist file."""
        missions = set()
        try:
            self.logger.debug("Opening %s", datalist)
            with open(datalist) as fh:
                for line in fh.readlines():
                    # MappingAUVOps2014/PortugueseLedge2008/Figures
                    # contains null characters
                    line = line.strip("\x00")
                    if not line.strip():
                        continue
                    if line.startswith("#") or line.startswith("$"):
                        continue
                    # '/mbari/SeafloorMapping/2019/AxialSeamount/Figures_v2019Oct31/AxialSummit_2006_Topo1mSq.mb-1'
                    # Remove leading 'P:'
                    line = line.lstrip("P:")
                    item = line.split()[0].strip()
                    item = re.sub(r"^\/Volumes", "/mbari", item)
                    if item.endswith("mb-1"):
                        # line is another file, recurse into it
                        try:
                            cpath, cfile = self._examine_mb1_line(
                                path,
                                datalist,
                                item,
                            )
                        except RecursionError as e:
                            self.logger.debug(e)
                            return list(missions), datalist
                        sub_missions, _ = self.missions_list(cpath, cfile)
                        missions.update(sub_missions)
                    elif re.match(r"(^[\.\/]*)(\S+)\s+(\d+)", line):
                        # line begins with optional relative or absolute path,
                        # then space and number - add paths to missions set
                        full_path = os.path.abspath(
                            os.path.join(
                                path,
                                os.path.dirname(item),
                            )
                        )
                        missions.add(full_path.replace(MBARI_DIR, ""))
                    else:
                        # line is likely missing the integer number following
                        # the space or is not a .mb-1 file
                        self.logger.info(
                            "Ignoring line: %s from %s",
                            line.strip(),
                            datalist,
                        )
        except FileNotFoundError:
            self.logger.debug("File not found: %s", datalist)
            if not os.path.exists(f"{MBARI_DIR}/MountCheck.cmd"):
                raise FileNotFoundError(f"{datalist}\nIs {MBARI_DIR} mounted?")
        return list(missions), datalist


# The columns in the .xlsx file are (as of 23 May 2024):
# Mission	Route	Location	Vehicle	Quality_category*	Patch_test	Repeat_survey	Quality_comment	Trackline_km	MGDS_compilation
# Dictionary below: key is field name in Mission model, value is column name in .xlsx file
col_lookup = {
    "name": "Mission",
    "route_file": "Route",
    "region_name": "Location",
    "vehicle_name": "Vehicle",
    "quality_categories": "Quality_category*",
    "patch_test": "Patch_test",
    "repeat_survey": "Repeat_survey",
    "quality_comment": "Quality_comment",
    "track_length": "Trackline_km",
    "mgds_compilation": "MGDS_compilation",
}


class SurveyTally(BaseLoader):
    """
    Satisfying https://github.com/mbari-org/SeafloorMappingDB/issues/206 requires
    a survey tally spreadsheet source file for hand editing of Mission information.
    """

    def read_xlsx_into_df(self, parent_dir: str) -> pd.DataFrame:
        xlsx_file = os.path.join(
            MBARI_DIR,
            parent_dir,
            "SMDB",
            f"SMDB_{parent_dir}_survey_tally.xlsx",
        )
        if not os.path.exists(xlsx_file):
            self.logger.debug(f"File {xlsx_file} not found")
            return pd.DataFrame(), xlsx_file
        if self.args.last_n_days:
            if os.path.getmtime(xlsx_file) < time() - self.args.last_n_days * 86400:
                self.logger.debug(
                    f"Skipping file {xlsx_file} older than {self.args.last_n_days = }"
                )
                return pd.DataFrame(), xlsx_file
        try:
            # Read the .xlsx file into a data frame
            self.logger.info(f"Reading {xlsx_file}")
            df = pd.read_excel(xlsx_file, engine="openpyxl")
            df = df.fillna("")  # Replace NaN with empty string
        except Exception as e:
            # An OSError will be raised if the file opened by someone in Excel
            self.logger.error(f"Error reading {xlsx_file}: {e}")
            return pd.DataFrame(), xlsx_file
        df = df.fillna("")  # Replace NaN with empty string

        # The df looks like (from print(df.head(2).to_csv(index=False))):
        # Mission,Route,Location,Vehicle,Quality_category*,Patch_test,Repeat_survey,Quality_comment,Trackline_km,MGDS_compilation
        # 20240510m1,20230814_1850Bend_SpindownPatchTest_1v2.rte,"1850m Bend, MBay",MAUV2,do_not_use_survey,x,,patch test; time stamp jumps back a day or calibrated snippets records likely crashed the multibeam processing; Edgetech data look strange.,,
        # 20240510m2,20230814_1850Bend_SpindownPatchTest_1v1.rte,"1850m Bend, MBay",MAUV1,never_run,,,Didn't have time,,
        self.logger.debug(f"Read {len(df)} rows from {xlsx_file}")
        return df, xlsx_file

    def update_db_from_df(self, df: pd.DataFrame, parent_dir: str) -> None:
        # Loop through rows in data frame and update the appropriate database fields
        count = 0
        saved_count = 0
        for _, row in df.iterrows():
            self.logger.debug(f"\n{row}")  # Printed in columns
            # Skip rows with no Mission name and with footnotes
            if not row["Mission"] or row["Mission"].startswith(
                "*Vocabulary for survey"
            ):
                continue
            try:
                count += 1
                # Get the Mission object for this row
                if row["Mission"].startswith(f"{parent_dir}/"):
                    mission = Mission.objects.get(name=row["Mission"])
                else:
                    mission = Mission.objects.get(name=f"{parent_dir}/{row['Mission']}")
                # Update the fields, mapping the column names to the Mission field names
                mission.route_file = row["Route"]
                mission.region_name = row["Location"]
                mission.vehicle_name = row["Vehicle"]
                mission.quality_comment = row["Quality_comment"]
                try:
                    mission.auv = row["AUV"] == "x"
                except KeyError:
                    pass
                try:
                    mission.lass = row["LASS"] == "x"
                except KeyError:
                    pass
                # If anything is in the Patch_test or Repeat_survey columns, set the field to True
                if row["Patch_test"]:
                    mission.patch_test = True
                if row["Repeat_survey"]:
                    mission.repeat_survey = True
                # mission.track_length = row["Trackline_km"]  # Do not update database with this field
                mission.mgds_compilation = row["MGDS_compilation"]
                mission.save()
                saved_count += 1
                self.logger.info(f"Updated fields for {mission.name = }")
                for st in row["Quality_category*"].split(" "):
                    if st:
                        try:
                            quality_category, _ = (
                                Quality_Category.objects.get_or_create(name=st)
                            )
                            mission.quality_categories.add(quality_category)
                        except ValueError:
                            self.logger.warning(
                                f"Quality_category* {quality_category} not in {[st[0] for st in Quality_Category.CHOICES]}"
                            )
                        self.logger.debug(f"Added {quality_category.name = }")
            except Mission.DoesNotExist:
                self.logger.warning(
                    f"Not found in database: {parent_dir}/{row['Mission']}"
                )
            except KeyError as e:
                self.logger.warning(f"KeyError: {e}")

        self.logger.info(
            f"Read {count} potential Missions to be updated from .xlsx file"
        )
        self.logger.info(f"Updated {saved_count} Missions in database")

    def process_xlsx(self) -> None:
        xlsx_files_processed = []
        for parent_dir in self.get_parent_dirs():
            self.logger.debug(f"Processing {parent_dir}")
            df, xlsx_file = self.read_xlsx_into_df(parent_dir)
            if not df.empty:
                self.update_db_from_df(df, parent_dir)
                xlsx_files_processed.append(xlsx_file)
        return xlsx_files_processed

    def get_parent_dirs(self) -> List[str]:
        """Return a list of parent directories to process. Check if they are in the database.
        If a parent_dir is specified, only return that one. Omit the '/mbari/SeafloorMapping/' prefix.
        """
        parent_dirs_in_db = {
            m.split("/")[0]
            for m in Mission.objects.values_list("name", flat=True).distinct()
        }
        parent_dirs = []
        if self.args.parent_dir:
            if os.path.isdir(os.path.join(MBARI_DIR, self.args.parent_dir)):
                if self.args.parent_dir in parent_dirs_in_db:
                    parent_dirs.append(self.args.parent_dir)
                else:
                    self.logger.warning(
                        f"Directory {self.args.parent_dir} not found in database {os.environ['DATABASE_URL']}"
                    )
            else:
                self.logger.warning(
                    f"Directory {self.args.parent_dir} not found in {MBARI_DIR}"
                )
        else:
            for f in os.listdir(MBARI_DIR):
                if os.path.isdir(os.path.join(MBARI_DIR, f)):
                    if f in parent_dirs_in_db:
                        parent_dirs.append(f)
                    else:
                        self.logger.debug(f"Directory {f} not found in database")
        return parent_dirs

    def read_from_db_into_rows(self, parent_dir: str) -> pd.DataFrame:
        # Check that the Mission model has all the fields in cols
        for col in col_lookup.keys():
            # col must match field names in the Mission table - to be cols in the .csv file
            if not hasattr(Mission, col):
                self.logger.warning(f"Mission model missing field: {col}")

        # Add rows for each mission
        rows = []
        for mission in Mission.objects.filter(name__startswith=parent_dir).order_by(
            "name"
        ):
            self.logger.debug(mission)
            row = []
            for col in col_lookup.keys():
                if col == "name":
                    item = getattr(mission, col).replace(f"{parent_dir}/", "")
                if col == "quality_categories":
                    item = " ".join([s.name for s in mission.quality_categories.all()])
                else:
                    if hasattr(mission, col):
                        item = getattr(mission, col, "") or ""
                    else:
                        item = ""
                row.append(str(item))
            rows.append(row)
        return col_lookup.keys(), rows

    def process_csv(self, xlsx_files_processed: List[str] = None):
        for parent_dir in self.get_parent_dirs():
            csv_dir = os.path.join(MBARI_DIR, parent_dir, "SMDB")
            if xlsx_files_processed != None:
                self.logger.debug(f"{xlsx_files_processed = }")
                if (
                    os.path.join(csv_dir, f"SMDB_{parent_dir}_survey_tally.xlsx")
                    not in xlsx_files_processed
                ):
                    self.logger.debug(
                        f"No .xlsx file processed for {parent_dir}. Skipping .csv file creation."
                    )
                    continue
            cols, rows = self.read_from_db_into_rows(parent_dir)
            if not os.path.exists(csv_dir):
                os.makedirs(csv_dir)
            csv_file = os.path.join(csv_dir, f"SMDB_{parent_dir}_survey_tally.csv")
            self.logger.debug(f"Writing {csv_file}")
            count = 0
            try:
                # Write the .csv file using the col_lookup dictionary so that they match the .xlsx file
                with open(csv_file, "w") as f:
                    f.write(",".join([col_lookup[c] for c in cols]) + "\n")
                    for row in rows:
                        count += 1
                        # Remove any commas in the fields
                        row = [r.replace(",", "") for r in row]
                        f.write(",".join(row) + "\n")
            except BlockingIOError as e:
                self.logger.error(e)
                self.logger.error(f"File {csv_file} might be opened in Excel ?")
            self.logger.info(f"Wrote {count} Missions to {csv_file}")


class ExcludeFile(BaseLoader):
    def read_config_exclude_list(self) -> None:
        if not self.exclude_paths:
            with open(self.args.exclude) as fh:
                for line in fh:
                    if line.startswith("/mbari/SeafloorMapping/"):
                        self.exclude_paths.add(line.strip())
            self.logger.info(
                f"Read {len(self.exclude_paths)} paths to exclude from {self.args.exclude}"
            )

    def read_exclude_path_xlsxs(self) -> None:
        """Walk the <parent_dir>/SMDB folders for files named <parent_dir>_exlude_list.xlsx'
        and load the rows into the exclude_paths set.  This is used to skip over directories
        that we don't want to process.
        """
        count = 0
        for parent_dir in os.listdir(MBARI_DIR):
            try:
                xlsx_file = os.path.join(
                    MBARI_DIR, parent_dir, "SMDB", f"{parent_dir}_exclude_list.xlsx"
                )
                if not os.path.exists(xlsx_file):
                    continue
                df = pd.read_excel(xlsx_file, engine="openpyxl")
                for path in df["path"]:
                    count += 1
                    self.exclude_paths.add(path)
            except (FileNotFoundError, NotADirectoryError, PermissionError) as e:
                self.logger.debug(f"Could not open {xlsx_file} for reading: {e}")
            self.logger.info(f"Read {count} paths to exclude from {xlsx_file}")

    def write_exclude_path_csvs(self) -> None:
        """Write the exclude_paths to <parent_dir>/SMDB/exlude_list_<parent_dir>.csv files"""
        # This method may only need to be run once to create the <parent_dir> exclude files from
        # the original exclude.list file maintained in the git repo in smdb/config/exclude.list

        # Build hash of paths keyed by parent_dir
        pd_hash = {}
        for path in sorted(self.exclude_paths):
            parent_dir = path.split(MBARI_DIR)[1].split("/")[0]
            if parent_dir not in pd_hash:
                pd_hash[parent_dir] = []
            pd_hash[parent_dir].append(path)
        # Write out the exclude files
        for parent_dir, paths in pd_hash.items():
            if not os.path.isdir(os.path.join(MBARI_DIR, parent_dir)):
                self.logger.warning("No directory found for %s", parent_dir)
            csv_file = os.path.join(
                MBARI_DIR, parent_dir, "SMDB", f"{parent_dir}_exclude_list.csv"
            )
            with open(csv_file, "w") as fh:
                fh.write("path\n")
                for path in paths:
                    fh.write(f"{path}\n")
            self.logger.info(f"Wrote {len(paths)} paths to {csv_file}")

    def write_consolidated_exclude_list(self) -> None:
        """Write the consolidated exclude paths to exclude_list.txt next to the load log file"""
        ds = DefaultStorage()
        ds.delete(self.MEDIA_EXCLUDE_LIST_FILE)
        with ds.open(self.MEDIA_EXCLUDE_LIST_FILE, "w") as fh:
            for path in sorted(self.exclude_paths):
                fh.write(f"{path}\n")
        self.logger.info(
            f"Wrote {len(self.exclude_paths)} paths to {self.MEDIA_EXCLUDE_LIST_FILE}"
        )


def run(*args):
    # Possible use: https://django-extensions.readthedocs.io/en/latest/runscript.html
    bl = BaseLoader()
    bl.process_command_line()
    bl.logger.debug("Arguments passed to run(): %s", " ".join(args))
    if bl.args.bootstrap and bl.args.notes and bl.args.fnv:
        exclude_file_load()
        missions_saved = bootstrap_load()
        notes_load(missions_saved)
        fnv_load(missions_saved)
    elif bl.args.bootstrap and bl.args.notes:
        exclude_file_load()
        missions_saved = bootstrap_load()
        notes_load(missions_saved)
    elif bl.args.bootstrap:
        exclude_file_load()
        missions_saved = bootstrap_load()
    elif bl.args.notes:
        notes_load(missions_saved)
    elif bl.args.mbinfo:
        mbinfo_load()
    elif bl.args.fnv:
        fnv_load()
    elif bl.args.compilation:
        compilation_load()
    elif bl.args.spreadsheets:
        spreadsheets_load()
    else:
        exclude_paths = exclude_file_load()
        missions_saved = bootstrap_load(exclude_paths)
        notes_load(missions_saved)
        fnv_load(missions_saved)
        compilation_load()
        bl.logger.info(f"Executing spreadsheets_load()")
        spreadsheets_load()
    bl.save_logger_output()


def exclude_file_load():
    ef = ExcludeFile()
    ef.process_command_line()
    ef.read_config_exclude_list()
    ef.read_exclude_path_xlsxs()
    ef.write_exclude_path_csvs()
    ef.write_consolidated_exclude_list()
    return ef.exclude_paths


def bootstrap_load(exclude_paths) -> list:
    bs = BootStrapper()
    bs.exclude_paths = exclude_paths
    bs.process_command_line()
    bs.load_from_grds()
    return bs.missions_saved


def notes_load(missions_saved: list):
    np = NoteParser()
    np.process_command_line()
    np.parse_notes(missions_saved)


def mbinfo_load():
    mbs = MBSystem()
    mbs.process_command_line()
    mbs.update_missions("mbinfo_update_mission_data")


def fnv_load(missions_saved: list = None):
    fnv = FNVLoader()
    fnv.process_command_line()
    fnv.update_missions("fnv_update_mission_data", missions_saved)


def compilation_load():
    comp = Compiler()
    comp.process_command_line()
    comp.link_compilation_to_missions()


def spreadsheets_load():
    st = SurveyTally()
    st.process_command_line()
    xlsx_files_processed = st.process_xlsx()
    if st.args.parent_dir:
        # Only process the .csv file for the specified parent_dir
        st.process_csv(xlsx_files_processed)
    else:
        st.process_csv()


if __name__ == "__main__":
    run()
