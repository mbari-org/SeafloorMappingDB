"""
Seed one mission with demo citations so you can see the Citations UI
(mission detail page and Missions page citation filter).

Usage:
  python manage.py seed_citation_demo
  python manage.py seed_citation_demo --mission "2019/20190124m1"

Requires at least one Mission in the DB (e.g. load fixtures first:
  python manage.py loaddata missions_notes_5.json).
"""
from django.core.management.base import BaseCommand

from smdb.models import Citation, Mission


DEMO_CITATIONS = [
    {"doi": "10.5678/seafloor-mapping-2020", "full_reference": "Smith et al. 2020, Seafloor mapping methods."},
    {"doi": "10.1234/auv-survey", "full_reference": ""},
]


class Command(BaseCommand):
    help = "Attach demo citations to one mission so you can see the Citations UI."

    def add_arguments(self, parser):
        parser.add_argument(
            "--mission",
            type=str,
            default=None,
            help="Mission name (e.g. 2019/20190124m1). If omitted, use first mission.",
        )

    def handle(self, *args, **options):
        mission_name = options["mission"]
        if mission_name:
            try:
                mission = Mission.objects.get(name=mission_name)
            except Mission.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"Mission not found: {mission_name}"))
                return
        else:
            mission = Mission.objects.order_by("name").first()
            if not mission:
                self.stderr.write(
                    self.style.ERROR("No missions in DB. Run: python manage.py loaddata missions_notes_5.json")
                )
                return
            mission_name = mission.name

        mission.citations.clear()
        for item in DEMO_CITATIONS:
            citation, _ = Citation.objects.get_or_create(
                doi=item["doi"],
                defaults={"full_reference": item["full_reference"] or ""},
            )
            if item["full_reference"]:
                citation.full_reference = item["full_reference"]
                citation.save()
            mission.citations.add(citation)

        self.stdout.write(
            self.style.SUCCESS(
                f"Added {len(DEMO_CITATIONS)} demo citations to mission: {mission_name}"
            )
        )
        self.stdout.write(
            f"  Mission detail: /missions/{mission.slug}/\n"
            f"  Missions (filter): /missions/"
        )
