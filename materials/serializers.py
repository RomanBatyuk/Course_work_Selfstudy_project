from rest_framework import serializers

from materials.models import Lesson, Section


class SectionSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для раздела(Section).
    """

    class Meta:
        model = Section
        fields = "__all__"


class LessonSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для урока(Lesson).
    """

    class Meta:
        model = Lesson
        fields = "__all__"
