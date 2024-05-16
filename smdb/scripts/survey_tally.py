#!/usr/bin/python
"""
Create a survey tally spreadsheet source file for hand editing of Mission information.
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
import logging  # noqa F402
from netCDF4 import Dataset  # noqa F402
from datetime import date, datetime, timedelta  # noqa F402
from dateutil.parser import ParserError, parse  # noqa F402
from django.conf import settings  # noqa F402
from django.core.files import File  # noqa F402
from django.core.files.base import ContentFile  # noqa F402
from django.core.files.storage import DefaultStorage  # noqa F402
from django.contrib.gis.geos import Point, Polygon, LineString  # noqa F402
from glob import glob
import pandas as pd  # noqa F402
from PIL import Image, UnidentifiedImageError  # noqa F402
from smdb.models import (
    Compilation,
    Expedition,
    Mission,
    Platform,
    Platformtype,
)  # noqa F402
from subprocess import check_output, TimeoutExpired  # noqa F402
from time import time  # noqa F402

MBARI_DIR = "/mbari/SeafloorMapping/"
col_lookup = {
    "name": "Mission",
    "route_file": "Route",
    "region_name": "Location",
    "vehicle_name": "Vehicle",
    "quality_comment": "Comment",
    "auv": "AUV",
    "lass": "LASS",
    "status": "Status*",
    "patch_test": "Patch_test**",
    "track_length": "km of trackline",
    "mgds_compilation": "MGDS_compilation",
}

instructions = f"""
Satisfying https://github.com/mbari-org/SeafloorMappingDB/issues/206 requires
a survey tally spreadsheet source file for hand editing of Mission information.

"""


class SurveyTally:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._log_levels = (logging.WARN, logging.INFO, logging.DEBUG)
        self._log_strings = ("WARN", "INFO", "DEBUG")
        self.commandline = None

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
        # Specify year and whether reading .xlsx or writing .csv
        parser.add_argument(
            "--parent_dir",
            action="store",
            help=f"Read or write a .xlsx or .csv file for the direct sub-directory of {MBARI_DIR}",
        )
        parser.add_argument(
            "--read_xlsx",
            action="store_true",
            help="Read an .xlsx file for the Missions in parent_dir and update the database",
        )
        parser.add_argument(
            "--write_csv",
            action="store_true",
            help="Write a .csv file with database values for the Missions in parent_dir",
        )
        parser.add_argument(
            "--last_n_days",
            type=float,
            help="Read the last n days of Missions",
        )

        self.commandline = " ".join(sys.argv)
        self.args = parser.parse_args()  # noqa

    def setup_logging(self):
        logging.getLogger().handlers.clear()
        _formatter = logging.Formatter(
            "%(levelname)s %(asctime)s %(filename)s "
            "%(funcName)s():%(lineno)d %(message)s"
        )
        self._handler = logging.StreamHandler()
        self._handler.setFormatter(_formatter)
        self.logger.addHandler(self._handler)
        self.logger.setLevel(self._log_levels[self.args.verbose])

        self.logger.debug(
            "Using database at DATABASE_URL = %s", os.environ["DATABASE_URL"]
        )

    def read_xlsx_into_df(self, parent_dir: str) -> pd.DataFrame:
        xlsx_file = os.path.join(
            MBARI_DIR,
            parent_dir,
            "SMDB",
            f"SMDB_{parent_dir}_survey_tally.xlsx",
        )
        if self.args.last_n_days:
            if os.path.getmtime(xlsx_file) < time() - self.args.last_n_days * 86400:
                self.logger.debug(
                    f"Skipping file {xlsx_file} older than {self.args.last_n_days = }"
                )
                return pd.DataFrame()
        self.logger.info(f"Reading {xlsx_file}")
        try:
            df = pd.read_excel(xlsx_file, engine="openpyxl")
        except FileNotFoundError:
            self.logger.warning(f"File {xlsx_file} not found")
            return pd.DataFrame()
        df = pd.read_excel(xlsx_file, engine="openpyxl")
        df = df.fillna("")  # Replace NaN with empty string

        # The df (from sheet index_col=0) looks like (from print(df.head(2).to_csv())):
        # Mission,Route,Location,Vehicle,Comment,AUV,LASS,Status*,Patch_test**,km of trackline,MGDS_compilation
        # 20230310m1,PuyDesFolles_1v7,MAR PdF,MAUV1,pressure-depth problem with code,x,,production_survey,,78.4,FKt230303_MBARI_AUV
        # 20230310m2,PuyDesFolles_2v7,MAR PdF,MAUV2,pressure-depth problem with code,x,,production_survey,,79.6,FKt230303_MBARI_AUV
        return df

    def update_db_from_df(self, df: pd.DataFrame, parent_dir: str) -> None:
        # Loop through rows in data frame and update the appropriate database fields
        for index, row in df.iterrows():
            self.logger.debug(f"\n{row}")  # Printed in columns
            try:
                # Get the Mission object for this row
                mission = Mission.objects.get(name=f"{parent_dir}/{row['Mission']}")
                # Update the fields, mapping the column names to the Mission field names
                mission.route_file = row["Route"]
                mission.region_name = row["Location"]
                mission.vehicle_name = row["Vehicle"]
                mission.quality_comment = row["Comment"]
                mission.auv = str(row["AUV"]) == "x"
                mission.lass = str(row["LASS"]) == "x"
                mission.status = row["Status*"] or ""
                mission.patch_test = str(row["Patch_test**"]) == "patch_test"
                # mission.track_length = row["km of trackline"]
                mission.mgds_compilation = row["MGDS_compilation"]
                mission.save()
                self.logger.info(f"Updated {mission}")
            except Mission.DoesNotExist:
                self.logger.warning(f"Mission {row['Mission']} not found in database")

    def process_xlsx(self) -> None:
        for parent_dir in self.get_parent_dirs():
            self.logger.info(f"Processing {parent_dir}")
            df = self.read_xlsx_into_df(parent_dir)
            self.update_db_from_df(df, parent_dir)

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
        # cols must match field names in the Mission table - to be cols in the .csv file
        cols = [
            "name",  # Saved without the parent_dir suffix
            "route_file",  # Originally "route"
            "region_name",  # Originally "location"
            "vehicle_name",  # Originally "vehicle"
            "quality_comment",  # Originally "comment"
            "auv",  # Boolean
            "lass",  # Boolean
            "status",  # Controlled vocabulary: "production_survey", "test_survey", "failed_survey", "use_with_caution"
            "patch_test",  # String: "patch_test" or ""
            "track_length",  # Originally "km of trackline" - should use values computed from --fnv
            "mgds_compilation",  # Srting: e.g. "FKt230303_MBARI_AUV"
        ]
        # Check that the Mission model has all the fields in cols
        for col in cols:
            if not hasattr(Mission, col):
                self.logger.warning(f"Mission model missing field: {col}")

        # Add rows for each mission
        rows = []
        for mission in Mission.objects.filter(name__startswith=parent_dir):
            self.logger.debug(mission)
            row = []
            for col in cols:
                if col == "name":
                    item = getattr(mission, col).replace(f"{parent_dir}/", "")
                else:
                    if hasattr(mission, col):
                        item = getattr(mission, col, "") or ""
                    else:
                        item = ""
                row.append(str(item))
            rows.append(row)
        return cols, rows

    def process_csv(self):
        for parent_dir in self.get_parent_dirs():
            cols, rows = self.read_from_db_into_rows(parent_dir)
            csv_dir = os.path.join(MBARI_DIR, parent_dir, "SMDB")
            if not os.path.exists(csv_dir):
                os.makedirs(csv_dir)
            csv_file = os.path.join(csv_dir, f"SMDB_{parent_dir}_survey_tally.csv")
            self.logger.info(f"Writing {csv_file}")
            # Write the .csv file using the col_lookup dictionary so that they match the .xlsx file
            with open(csv_file, "w") as f:
                f.write(",".join([col_lookup[c] for c in cols]) + "\n")
                for row in rows:
                    f.write(",".join(row) + "\n")


if __name__ == "__main__":
    st = SurveyTally()
    st.process_command_line()
    st.setup_logging()
    if st.args.read_xlsx:
        st.process_xlsx()
    elif st.args.write_csv:
        st.process_csv()
    else:
        st.logger.error("No action specified. Use --read_xlsx or --write_csv")
    sys.exit(0)
