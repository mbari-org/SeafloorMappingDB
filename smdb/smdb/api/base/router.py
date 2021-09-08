from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from smdb.users.api.views import UserViewSet

from . import views

if settings.DEBUG:
    router = DefaultRouter() # pragma: no cover
else:
    router = SimpleRouter()

router.register("users", UserViewSet)
router.register("missiontype", views.MissionTypeViewSet)
router.register("persons", views.PersonViewSet)
router.register("platformtype", views.PlatformTypeViewSet)

app_name = "api"
urlpatterns = router.urls
