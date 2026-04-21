"""
Management command: check_migration_health
Exits non-zero if any migrations are unapplied, printing a clear list.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS, connections
from django.db.migrations.executor import MigrationExecutor


class Command(BaseCommand):
    help = "Check for unapplied migrations and optionally apply them."

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Apply unapplied migrations instead of just reporting them.",
        )

    def handle(self, *args, **options):
        connection = connections[DEFAULT_DB_ALIAS]
        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()
        plan = executor.migration_plan(targets)

        if not plan:
            self.stdout.write(self.style.SUCCESS("All migrations applied. Database is up to date."))
            return

        self.stdout.write(self.style.WARNING(f"{len(plan)} unapplied migration(s):"))
        for migration, _ in plan:
            self.stdout.write(f"  [ ] {migration.app_label}.{migration.name}")

        if options["apply"]:
            self.stdout.write("Applying migrations...")
            call_command("migrate", "--noinput", verbosity=1)
            self.stdout.write(self.style.SUCCESS("Done."))
            return

        self.stdout.write(
            self.style.ERROR(
                "Run 'python manage.py migrate --noinput' or "
                "'python manage.py check_migration_health --apply' to fix."
            )
        )
        raise SystemExit(1)
