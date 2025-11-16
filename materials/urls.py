from django.urls import path

from materials.apps import MaterialsConfig
from materials.views import (
    LessonDetailView,
    LessonListView,
    LessonTestView,
    ProfileView,
    SectionDetailView,
)

from rest_framework.routers import DefaultRouter

from materials.views import LessonViewSet, SectionViewSet

app_name = MaterialsConfig.name

router = DefaultRouter()
router.register(r"sections", SectionViewSet)
router.register(r"lessons", LessonViewSet)

urlpatterns = [
    path("", ProfileView.as_view(), name="home"),
    path("section/<int:pk>/", SectionDetailView.as_view(), name="section_detail"),
    path("lesson/", LessonListView.as_view(), name="lesson_list"),
    path("lesson/<int:pk>/", LessonDetailView.as_view(), name="lesson_detail"),
    path("lessons/<int:lesson_id>/test/", LessonTestView.as_view(), name="lesson_test"),
]

urlpatterns += router.urls
