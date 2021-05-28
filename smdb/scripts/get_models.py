"""
For testing django-extensions's runscript:
    docker-compose run --rm django python manage.py runscript get_models
"""

from smdb.models import Mission

def run():
    miss = Mission.objects.all()
    print(miss)
