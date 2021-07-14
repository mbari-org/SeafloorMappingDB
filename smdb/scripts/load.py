#!/usr/bin/python
"""
Scan SeafloorMapping share for data to load into smdb
"""

import os
import sys

parentDir = os.path.join(os.path.dirname(__file__), "../")
sys.path.insert(0, parentDir)

import argparse
import django
import math
import subprocess

os.environ["DJANGO_SETTINGS_MODULE"] = f"config.settings.{os.environ['BUILD_ENV']}"
django.setup()

import logging
import pathspec
from netCDF4 import Dataset
from django.contrib.gis.geos import Polygon
from smdb.models import Mission, Expedition

instructions = f"""
Can be run from smdb Docker environment thusly...
    First time - install necessary things:
        git clone git@github.com:mbari-org/SeafloorMappingDB.git
        cd SeafloorMappingDB
        export SMDB_HOME=$(pwd)
        export COMPOSE_FILE=$SMDB_HOME/smdb/local.yml
        docker-compose up -d
    Thereafter:
        cd SeafloorMappingDB
        export SMDB_HOME=$(pwd)
        export COMPOSE_FILE=$SMDB_HOME/smdb/local.yml
        docker-compose run --rm -u 399 -v /mbari/SeafloorMapping:/mbari/SeafloorMapping django {__file__} -v
        (Replace '399' with your MBARI user id, what `id -u` returns.)
"""


class Scanner:
    logger = logging.getLogger(__name__)
    _log_levels = (logging.WARN, logging.INFO, logging.DEBUG)
    _log_strings = ("WARN", "INFO", "DEBUG")

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
            self.logger.debug(f"Checking if point is on Earth: {point}")
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
            self.logger.warn(f"{fp} does not have attribute descrtion nor source")

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
            "-f",
            "--file",
            action="store",
            help="Input file containing list of ZTopo.grd files",
        )

        self.args = parser.parse_args()
        self.commandline = " ".join(sys.argv)

        # Override Django's logging so that we can setLevel() with --verbose
        logging.getLogger().handlers.clear()
        _handler = logging.StreamHandler()
        _formatter = logging.Formatter(
            "%(levelname)s %(asctime)s %(filename)s "
            "%(funcName)s():%(lineno)d %(message)s"
        )
        _handler.setFormatter(_formatter)
        self.logger.addHandler(_handler)
        self.logger.setLevel(self._log_levels[self.args.verbose])

        self.logger.debug(
            f"Using database at DATABASE_URL =" f" {os.environ['DATABASE_URL']}"
        )


def run(*args):
    print(" ".join(args))
    sc = Scanner()
    sc.process_command_line()

    # Avoid ._ZTopo.grd and ZTopo.grd.cmd files with regex locate
    locate_cmd = ("locate -d /etc/smdb/SeafloorMapping.db -r '\/ZTopo.grd$'")
    for fp in subprocess.getoutput(locate_cmd).split('\n'):
        sc.logger.info(f"file: {fp}")
        if fp.endswith("ZTopo.grd"):
            try:
                ds = Dataset(fp)
                sc.logger.debug(ds)
            except PermissionError as e:
                sc.logger.warning(f"{e}")
            if not sc.is_geographic(ds):
                sc.logger.warn(f"{fp} is not Projection: Geographic")
                continue
            try:
                grid_bounds = sc.extent(ds, fp)
            except ValueError as e:
                sc.logger.warning(e)
                continue

            sc.logger.info(f"grid_bounds: {grid_bounds:}")

            expedition, _ = Expedition.objects.get_or_create(
                expd_path_name=os.path.dirname(fp)
            )
            mission = Mission(
                mission_name=fp.replace("/mbari/SeafloorMapping/", "").replace(
                    "ZTopo.grd", ""
                ),
                expedition=expedition,
                grid_bounds=grid_bounds,
            )
            mission.save()
            sc.logger.info(f"Saved {mission}")


if __name__ == "__main__":
    run()
