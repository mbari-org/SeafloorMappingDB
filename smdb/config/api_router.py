from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from smdb.users.api.views import UserViewSet
from smdb.api.views import MissionTypeViewSet, PersonViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
##router.register("missions", MissionViewSet)
router.register("missiontypes", MissionTypeViewSet)
router.register("persons", PersonViewSet)


app_name = "api"
urlpatterns = router.urls
