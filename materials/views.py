from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView, TemplateView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from materials.models import Answer, Lesson, Section
from materials.paginators import PaginationList
from materials.permissions import IsAdminOrTeacher
from materials.serializers import LessonSerializer, SectionSerializer


class SectionViewSet(viewsets.ModelViewSet):
    """
    CRUD разделов для postman.
    """

    queryset = Section.objects.all()
    serializer_class = SectionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    pagination_class = PaginationList

    def get_queryset(self):
        user = self.request.user
        # Если пользователь в группе 'Admin', показываем все разделы
        if user.groups.filter(name="Admin").exists():
            return Section.objects.all()
        # Если в группе 'Teacher', показываем только свои (где owner == user)
        elif user.groups.filter(name="Teacher").exists():
            return Section.objects.filter(owner=user)
        # Для других групп (например, Student) — ничего или пустой queryset
        else:
            return Section.objects.none()


class LessonViewSet(viewsets.ModelViewSet):
    """
    CRUD уроков для postman.
    """

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticated, IsAdminOrTeacher]
    pagination_class = PaginationList

    def get_queryset(self):
        user = self.request.user
        # Если пользователь в группе 'Admin', показываем все разделы
        if user.groups.filter(name="Admin").exists():
            return Lesson.objects.all()
        # Если в группе 'Teacher', показываем только свои (где owner == user)
        elif user.groups.filter(name="Teacher").exists():
            return Lesson.objects.filter(owner=user)
        # Для других групп (например, Student) — ничего или пустой queryset
        else:
            return Lesson.objects.none()


class ProfileView(LoginRequiredMixin, TemplateView):
    """
    Страница показывает все разделы с уроками на главной странице (home.html).
    """

    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Загружаем все разделы с уроками
        sections = Section.objects.prefetch_related("lessons")
        context["sections"] = sections
        return context


class SectionDetailView(DetailView):
    """
    Детальная страница раздела: показывает уроки раздела.
    """

    model = Section
    template_name = "section_detail.html"
    context_object_name = "section"

    def get_queryset(self):
        return Section.objects.prefetch_related("lessons")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        section = self.object

        lessons_queryset = section.lessons.all().order_by('name')

        paginator = Paginator(lessons_queryset, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        context['paginator'] = paginator
        context['is_paginated'] = page_obj.has_other_pages()

        return context


class LessonListView(ListView):
    """
    Список уроков в разделе.
    """

    model = Lesson
    context_object_name = "lessons"

    def get_section(self):
        """
        Получаем секцию по pk из kwargs. Поднимаем Http404, если pk отсутствует или секция не найдена.
        """
        if "pk" not in self.kwargs:
            raise Http404("Section pk is required")
        try:
            return Section.objects.get(pk=self.kwargs["pk"])
        except Section.DoesNotExist:
            raise Http404("Section not found")

    def get_queryset(self):
        section = self.get_section()
        # Уроки раздела
        return Lesson.objects.filter(section=section)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["section"] = self.get_section()
        return context


class LessonDetailView(DetailView):
    """
    Детальная страница урока.
    """

    model = Lesson
    template_name = "lesson_detail.html"
    context_object_name = "lesson"

    def get_queryset(self):
        return Lesson.objects.all()


class LessonTestView(TemplateView):
    template_name = "lesson_test.html"

    def get_context_data(self, lesson_id, **kwargs):
        context = super().get_context_data(**kwargs)
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        questions = lesson.questions.all().order_by("order")

        # Загружаем вопросы с ответами
        questions_with_answers = []
        for question in questions:
            answers = list(question.answers.all())  # Список для манипуляций
            # Для случайного порядка ответов (опционально): import random; random.shuffle(answers)
            questions_with_answers.append(
                {
                    "question": question,
                    "answers": answers,
                }
            )

        context["lesson"] = lesson
        context["questions_with_answers"] = questions_with_answers
        context["results"] = None
        return context

    def post(self, request, lesson_id):
        lesson = get_object_or_404(Lesson, pk=lesson_id)
        questions = lesson.questions.all().order_by("order")

        results = []
        correct_count = 0
        total_questions = questions.count()

        for question in questions:
            selected_answer_id = request.POST.get(f"answer_{question.id}")
            if selected_answer_id:
                try:
                    selected_answer = Answer.objects.get(
                        pk=selected_answer_id, question=question
                    )
                    correct_answer = question.answers.filter(is_correct=True).first()
                    is_correct = selected_answer.is_correct
                    if is_correct:
                        correct_count += 1
                    results.append(
                        {
                            "question": question,
                            "selected": selected_answer,
                            "correct": correct_answer,
                            "is_correct": is_correct,
                        }
                    )
                except Answer.DoesNotExist:
                    pass

        # Рассчитываем процент
        percentage = (
            (correct_count / total_questions * 100) if total_questions > 0 else 0
        )

        # Передаём в контекст для отображения
        context = self.get_context_data(lesson_id)
        context["results"] = results
        context["correct_count"] = correct_count
        context["total_questions"] = total_questions
        context["percentage"] = round(percentage, 1)  # Округление до 1 знака

        # Опционально: Сообщение для пользователя
        messages.success(
            request,
            f"Тест завершён! Правильных ответов: {correct_count}/{total_questions} ({percentage:.1f}%)",
        )

        return self.render_to_response(context)
