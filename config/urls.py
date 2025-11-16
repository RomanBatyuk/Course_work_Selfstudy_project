from django.contrib import admin
from django.urls import path, include
from materials.views import ProfileView
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Course_work_Self-study_project",
      default_version='v1',
      description="Платформа для самообучения студентов",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="examplemail@yandex.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("materials.urls", namespace="materials")),
    path("accounts/", include('users.urls', namespace='accounts')),
    path("users/", include("users.urls", namespace="users")),
    path("accounts/profile/", ProfileView.as_view(), name="profile"),
    path("swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
