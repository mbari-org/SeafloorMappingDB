from smdb.models import Mission

def run():
    miss = Mission.objects.all()
    print(miss)
