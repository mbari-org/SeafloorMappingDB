from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from graphene_django.views import GraphQLView
from rest_framework.authtoken.views import obtain_auth_token

from smdb.api.base import router as api_v1_router
from smdb.views import (
    CompilationDetailView,
    CompilationTableView,
    ExpeditionDetailView,
    ExpeditionTableView,
    MissionDetailView,
    MissionTableView,
    MissionOverView,
)

GraphQLView.graphiql_template = "graphene_graphiql_explorer/graphiql.html"

urlpatterns = [
    path("", MissionOverView.as_view(), name="home"),
    path(
        "about/", TemplateView.as_view(template_name="pages/about.html"), name="about"
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("smdb.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    path("missions/", MissionTableView.as_view()),
    path(
        "missions/<str:slug>/",
        MissionDetailView.as_view(),
        name="mission-detail",
    ),
    path("expeditions/", ExpeditionTableView.as_view()),
    path(
        "expeditions/<str:slug>/",
        ExpeditionDetailView.as_view(),
        name="expedition-detail",
    ),
    path("compilations/", CompilationTableView.as_view()),
    path(
        "compilations/<str:slug>/",
        CompilationDetailView.as_view(),
        name="compilation-detail",
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# API URLS
urlpatterns += [
    # API base url
    path("api/v1/", include(api_v1_router)),
    # DRF auth token
    path("auth-token/", obtain_auth_token),
    path("graphql", csrf_exempt(GraphQLView.as_view(graphiql=True))),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
