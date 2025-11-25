from django.db import models


class Section(models.Model):
    name = models.CharField(
        max_length=50,
        verbose_name="Название раздела",
        help_text="Введите название раздела",
    )
    description = models.TextField(
        blank=True, null=True, verbose_name="Описание", help_text="Введите описание"
    )
    owner = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, verbose_name="Владелец"
    )

    class Meta:
        verbose_name = "Раздел"
        verbose_name_plural = "Разделы"


class Lesson(models.Model):
    name = models.CharField(
        max_length=50, verbose_name="Название урока", help_text="Введите название урока"
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание",
        help_text="Введите описание урока",
    )
    section = models.ForeignKey(
        Section, on_delete=models.CASCADE, related_name="lessons", verbose_name="Раздел"
    )
    owner = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, verbose_name="Владелец"
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"


class Question(models.Model):
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="questions", verbose_name="Урок"
    )
    text = models.TextField(verbose_name="Текст вопроса", help_text="Введите вопрос")
    order = models.PositiveIntegerField(
        default=0, verbose_name="Порядок", help_text="Порядок отображения вопросов"
    )

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"
        ordering = ["order"]


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Вопрос",
    )
    text = models.CharField(
        max_length=200, verbose_name="Текст ответа", help_text="Введите вариант ответа"
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name="Правильный ответ",
        help_text="Отметьте, если это правильный вариант",
    )

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"
