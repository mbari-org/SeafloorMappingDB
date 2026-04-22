"""
Guard against model changes without a checked-in migration file.
"""

from io import StringIO

import pytest
from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

pytestmark = pytest.mark.django_db


def test_no_missing_migration_files():
    """Fail if any model change is missing a corresponding migration file."""
    out = StringIO()
    try:
        call_command(
            "makemigrations",
            "--check",
            "--dry-run",
            interactive=False,
            stdout=out,
            stderr=out,
        )
    except SystemExit:
        pytest.fail(
            "Model changes exist without a migration file. "
            "Run 'python manage.py makemigrations' and commit the result.\n"
            f"Details:\n{out.getvalue()}"
        )


def test_no_unapplied_smdb_migrations():
    """Fail when migration files exist but are not applied in this database."""
    executor = MigrationExecutor(connection)
    loader = executor.loader
    applied = loader.applied_migrations

    unapplied_smdb = sorted(
        migration
        for migration in loader.graph.nodes.keys()
        if migration[0] == "smdb" and migration not in applied
    )

    if unapplied_smdb:
        missing = "\n".join(f"{app}.{name}" for app, name in unapplied_smdb)
        pytest.fail(
            "Unapplied smdb migrations detected in this environment.\n"
            "Run 'python manage.py migrate smdb' before deploy.\n"
            f"Unapplied:\n{missing}"
        )
