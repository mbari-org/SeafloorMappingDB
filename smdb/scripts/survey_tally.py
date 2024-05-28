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
    Quality_Category,
)  # noqa F402
from subprocess import check_output, TimeoutExpired  # noqa F402
from time import time  # noqa F402

MBARI_DIR = "/mbari/SeafloorMapping/"
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
    "repeat_survey": "Patch_test",
    "quality_comment": "Quality_comment",
    "track_length": "Trackline_km",
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
        return df, xlsx_file

    def update_db_from_df(self, df: pd.DataFrame, parent_dir: str) -> None:
        # Loop through rows in data frame and update the appropriate database fields
        for index, row in df.iterrows():
            self.logger.debug(f"\n{row}")  # Printed in columns
            # Skip rows with no Mission name and with footnotes
            if not row["Mission"] or row["Mission"].startswith(
                "*Vocabulary for survey"
            ):
                continue
            try:
                # Get the Mission object for this row
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
                mission.patch_test = row["Patch_test"] == "x"
                mission.repeat_survey = row["Repeat_survey"] == "x"
                # mission.track_length = row["Trackline_km"]  # Do not update database with this field
                mission.mgds_compilation = row["MGDS_compilation"]
                mission.save()
                self.logger.info(f"Updated {mission.name = }")
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
                        self.logger.info(f"Added {quality_category.name = }")
            except Mission.DoesNotExist:
                self.logger.warning(f"Mission {row['Mission']} not found in database")

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
        for mission in Mission.objects.filter(name__startswith=parent_dir):
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
    xlsx_files_processed = []
    if st.args.read_xlsx:
        xlsx_files_processed = st.process_xlsx()
    elif st.args.write_csv:
        st.process_csv()
    else:
        xlsx_files_processed = st.process_xlsx()
        st.process_csv(xlsx_files_processed)
    sys.exit(0)
