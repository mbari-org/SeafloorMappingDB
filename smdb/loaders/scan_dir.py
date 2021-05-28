#!/usr/bin/python
"""
Scan SeafloorMapping share for data to load into smdb
"""

import argparse
import logging
import os
import pathspec
import sys
from netCDF4 import Dataset
from django.contrib.gis.geos import Polygon, Point

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
        docker-compose run --rm -u 399 -v /Volumes/SeafloorMapping:/Volumes/SeafloorMapping django python {__file__}
"""


class Scanner:
    logger = logging.getLogger("Scanner")
    _handler = logging.StreamHandler()
    _formatter = logging.Formatter(
        "%(levelname)s %(asctime)s %(filename)s "
        "%(funcName)s():%(lineno)d %(message)s"
    )
    _handler.setFormatter(_formatter)
    _log_levels = (logging.WARN, logging.INFO, logging.DEBUG)
    logger.addHandler(_handler)

    def traverse(self, path, ignore_files=None):
        if not os.path.exists(path):
            return
        if ignore_files is None:
            ignore_files = []

        for item in os.scandir(path):
            full_path = os.path.join(path, item.name)
            spec = pathspec.PathSpec.from_lines(
                pathspec.patterns.GitWildMatchPattern, ignore_files
            )
            self.logger.debug((f"Examing: {full_path}"))
            if spec.match_file(full_path):
                self.logger.debug("Ignoring %s", item)
                continue

            if item.is_dir():
                for result in self.traverse(item.path, ignore_files):
                    yield os.path.join(item.name, result)
            else:
                yield full_path

    def process_command_line(self):
        parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawTextHelpFormatter,
            epilog=instructions,
        )
        parser.add_argument(
            "--dir",
            action="store",
            help="Mount point for SeafloorMapping share",
            default="/Volumes/SeafloorMapping",
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
            + ", ".join(
                [f"{i}: {v}" for i, v, in enumerate(("WARN", "INFO", "DEBUG"))]
            ),
        )

        self.args = parser.parse_args()
        self.commandline = " ".join(sys.argv)
        self.logger.setLevel(self._log_levels[self.args.verbose])
        self.logger.debug(
            f"Using database at DATABASE_URL =" f" {os.environ['DATABASE_URL']}"
        )


if __name__ == "__main__":
    sc = Scanner()
    sc.process_command_line()
    sc.logger.info(f"Scanning directory {sc.args.dir}")
    ignore_patterns = [
        "\.*",
    ]
    for item in sc.traverse(sc.args.dir, ignore_patterns):
        sc.logger.debug(f"file: {item}")
        if item.endswith(".grd"):
            sc.logger.info(item)
            ds = Dataset(item)
            if "Projection: Geographic" in ds.description:
                sc.logger.info(ds)
                grid_bounds = Polygon(
                    (
                        (float(ds["lon"][0].data), float(ds["lat"][0].data)),
                        (float(ds["lon"][0].data), float(ds["lat"][-1].data)),
                        (float(ds["lon"][-1].data), float(ds["lat"][-1].data)),
                        (float(ds["lon"][-1].data), float(ds["lat"][0].data)),
                        (float(ds["lon"][0].data), float(ds["lat"][0].data)),
                    ),
                    srid=4326,
                )
                breakpoint()
