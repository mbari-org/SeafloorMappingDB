"""
Tests for scripts/load.py citation ingestion branches.

Covers:
  - New "Citations" column format  (doi|full_reference pairs separated by ";")
  - Legacy "Citation_1"/"Citation_2" column format (DOI extracted via regex)
  - Field truncation to respect max_length constraints
"""
import argparse
import logging

import pandas as pd
import pytest

from smdb.models import Citation, Expedition, Mission

pytestmark = pytest.mark.django_db()

# Minimum columns required by update_db_from_df (beyond Mission/Route/Citations)
BASE_ROW = {
    "Mission": "20140306m1",
    "Route": "",
    "Location": "",
    "Vehicle": "",
    "Quality_category*": "",
    "Quality_comment": "",
    "Patch_test": "",
    "Repeat_survey": "",
    "MGDS_compilation": "",
}


@pytest.fixture()
def survey_tally():
    """Return a minimally configured SurveyTally instance."""
    from scripts.load import SurveyTally

    st = SurveyTally()
    st.args = argparse.Namespace(
        spreadsheets=True,
        parent_dir=None,
        last_n_days=None,
        clobber=False,
        clobber_log_file=False,
        log_file=None,
        verbose=0,
    )
    st.logger = logging.getLogger("load")
    return st


@pytest.fixture()
def mission_2014(db):
    """Create a minimal Mission that belongs to the MappingAUVOps2014 parent dir."""
    exp, _ = Expedition.objects.get_or_create(name="MappingAUVOps2014")
    mission, _ = Mission.objects.get_or_create(
        name="MappingAUVOps2014/20140306m1",
        defaults={"expedition": exp},
    )
    return mission


# ---------------------------------------------------------------------------
# New "Citations" column format
# ---------------------------------------------------------------------------


def test_citations_column_creates_citation(survey_tally, mission_2014):
    """New pipe-separated Citations column creates Citation and links it to Mission."""
    row = {**BASE_ROW, "Citations": "10.1234/test|A test reference"}
    df = pd.DataFrame([row])
    survey_tally.update_db_from_df(df, "MappingAUVOps2014")

    assert Citation.objects.filter(doi="10.1234/test").exists()
    cit = Citation.objects.get(doi="10.1234/test")
    assert cit.full_reference == "A test reference"
    assert mission_2014.citations.filter(doi="10.1234/test").exists()


def test_citations_column_truncates_fields(survey_tally, mission_2014):
    """Overlong doi and full_reference are truncated before persisting."""
    long_doi = "x" * 300
    long_ref = "y" * 600
    row = {**BASE_ROW, "Citations": f"{long_doi}|{long_ref}"}
    df = pd.DataFrame([row])
    survey_tally.update_db_from_df(df, "MappingAUVOps2014")

    cit = Citation.objects.get(doi=long_doi[:256])
    assert len(cit.doi) == 256
    assert len(cit.full_reference) == 512


def test_citations_column_multiple_entries(survey_tally, mission_2014):
    """Semicolon-separated Citations column creates multiple Citation objects."""
    row = {**BASE_ROW, "Citations": "10.1/a|Ref A;10.2/b|Ref B"}
    df = pd.DataFrame([row])
    survey_tally.update_db_from_df(df, "MappingAUVOps2014")

    assert Citation.objects.filter(doi="10.1/a").exists()
    assert Citation.objects.filter(doi="10.2/b").exists()
    assert mission_2014.citations.count() == 2


# ---------------------------------------------------------------------------
# Legacy "Citation_1" / "Citation_2" column format
# ---------------------------------------------------------------------------


def test_legacy_citation_columns_doi_extraction(survey_tally, mission_2014):
    """DOI is extracted from a full reference string in Citation_1 column."""
    ref = (
        "Clague, D.A. et al. (2022). Some title, "
        "doi: 10.1016/j.jvolgeores.2022.107701"
    )
    row = {**BASE_ROW, "Citation_1": ref, "Citation_2": ""}
    df = pd.DataFrame([row])
    survey_tally.update_db_from_df(df, "MappingAUVOps2014")

    assert Citation.objects.filter(doi="10.1016/j.jvolgeores.2022.107701").exists()
    cit = Citation.objects.get(doi="10.1016/j.jvolgeores.2022.107701")
    assert cit.full_reference == ref[:512]
    assert mission_2014.citations.filter(doi="10.1016/j.jvolgeores.2022.107701").exists()


def test_legacy_citation_columns_two_citations(survey_tally, mission_2014):
    """Both Citation_1 and Citation_2 columns are loaded and linked."""
    ref1 = "Author A (2020). Title A, doi: 10.1000/aaa"
    ref2 = "Author B (2021). Title B, https://doi.org/10.2000/bbb"
    row = {**BASE_ROW, "Citation_1": ref1, "Citation_2": ref2}
    df = pd.DataFrame([row])
    survey_tally.update_db_from_df(df, "MappingAUVOps2014")

    assert Citation.objects.filter(doi="10.1000/aaa").exists()
    assert Citation.objects.filter(doi="10.2000/bbb").exists()
    assert mission_2014.citations.count() == 2


def test_legacy_citation_columns_truncation(survey_tally, mission_2014):
    """full_reference is truncated to 512 chars; doi fallback truncated to 256."""
    long_ref = "No DOI here " + "z" * 600
    row = {**BASE_ROW, "Citation_1": long_ref, "Citation_2": ""}
    df = pd.DataFrame([row])
    survey_tally.update_db_from_df(df, "MappingAUVOps2014")

    # With no DOI in the string the doi field falls back to ref_str[:256]
    expected_doi = long_ref[:256]
    assert Citation.objects.filter(doi=expected_doi).exists()
    cit = Citation.objects.get(doi=expected_doi)
    assert len(cit.full_reference) == 512


def test_legacy_citation_columns_empty_skipped(survey_tally, mission_2014):
    """Empty Citation_1 and Citation_2 values do not create any Citation."""
    row = {**BASE_ROW, "Citation_1": "", "Citation_2": ""}
    df = pd.DataFrame([row])
    survey_tally.update_db_from_df(df, "MappingAUVOps2014")

    assert mission_2014.citations.count() == 0
    assert Citation.objects.count() == 0
