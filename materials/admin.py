from django.contrib import admin

from materials.models import Answer, Lesson, Question, Section


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 1  # Количество пустых форм для ответов


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    inlines = [AnswerInline]  # Вопросы с ответами внутри


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ["name", "owner"]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ["name", "section", "owner"]
    inlines = [QuestionInline]  # Вопросы прямо в уроке
