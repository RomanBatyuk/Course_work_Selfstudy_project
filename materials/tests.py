from django.contrib.auth.models import Group
from django.test import Client, TestCase
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from materials.models import Answer, Lesson, Question, Section
from users.models import User


class SectionViewSetTest(APITestCase):
    def setUp(self):
        self.admin_group = Group.objects.create(name="Admin")
        self.teacher_group = Group.objects.create(name="Teacher")
        self.student_group = Group.objects.create(name="Student")

        self.admin_user = User.objects.create_user(
            email="admin@example.com", password="pass"
        )
        self.admin_user.groups.add(self.admin_group)

        self.teacher_user = User.objects.create_user(
            email="teacher@example.com", password="pass"
        )
        self.teacher_user.groups.add(self.teacher_group)

        self.student_user = User.objects.create_user(
            email="student@example.com", password="pass"
        )
        self.student_user.groups.add(self.student_group)

        self.section1 = Section.objects.create(
            name="Section 1", description="Desc 1", owner=self.teacher_user
        )
        self.section2 = Section.objects.create(
            name="Section 2", description="Desc 2", owner=self.admin_user
        )

        self.client = APIClient()

    def test_admin_can_retrieve_section(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f"/sections/{self.section1.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Section 1")

    def test_teacher_can_retrieve_own_section(self):
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.get(f"/sections/{self.section1.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teacher_cannot_retrieve_other_section(self):
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.get(f"/sections/{self.section2.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_update_section(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "name": "Updated Section",
            "description": "Updated Desc",
            "owner": self.admin_user.id,
        }
        response = self.client.put(f"/sections/{self.section1.pk}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.section1.refresh_from_db()
        self.assertEqual(self.section1.name, "Updated Section")

    def test_teacher_can_update_own_section(self):
        self.client.force_authenticate(user=self.teacher_user)
        data = {
            "name": "Updated by Teacher",
            "description": "Desc",
            "owner": self.teacher_user.id,
        }
        response = self.client.put(f"/sections/{self.section1.pk}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teacher_cannot_update_other_section(self):
        self.client.force_authenticate(user=self.teacher_user)
        data = {"name": "Hacked", "description": "Desc", "owner": self.teacher_user.id}
        response = self.client.put(f"/sections/{self.section2.pk}/", data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_delete_section(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f"/sections/{self.section1.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Section.objects.filter(pk=self.section1.pk).exists())

    def test_teacher_can_delete_own_section(self):
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.delete(f"/sections/{self.section1.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_teacher_cannot_delete_other_section(self):
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.delete(f"/sections/{self.section2.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_list_all_sections(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/sections/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_teacher_can_list_own_sections(self):
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.get("/sections/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Section 1")

    def test_student_can_list_no_sections(self):
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get("/sections/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access(self):
        response = self.client.get("/sections/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_section_as_teacher(self):
        self.client.force_authenticate(user=self.teacher_user)
        data = {
            "name": "New Section",
            "description": "New Desc",
            "owner": self.teacher_user.id,
        }
        response = self.client.post("/sections/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class LessonViewSetTest(APITestCase):
    def setUp(self):
        self.admin_group = Group.objects.create(name="Admin")
        self.teacher_group = Group.objects.create(name="Teacher")
        self.student_group = Group.objects.create(name="Student")

        self.admin_user = User.objects.create_user(
            email="admin@example.com", password="pass"
        )
        self.admin_user.groups.add(self.admin_group)

        self.teacher_user = User.objects.create_user(
            email="teacher@example.com", password="pass"
        )
        self.teacher_user.groups.add(self.teacher_group)

        self.student_user = User.objects.create_user(
            email="student@example.com", password="pass"
        )
        self.student_user.groups.add(self.student_group)

        self.section = Section.objects.create(
            name="Test Section", description="Desc", owner=self.teacher_user
        )
        self.lesson1 = Lesson.objects.create(
            name="Lesson 1",
            description="Desc 1",
            section=self.section,
            owner=self.teacher_user,
        )
        self.lesson2 = Lesson.objects.create(
            name="Lesson 2",
            description="Desc 2",
            section=self.section,
            owner=self.admin_user,
        )

        self.client = APIClient()

    def test_admin_can_list_all_lessons(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get("/lessons/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_teacher_can_list_own_lessons(self):
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.get("/lessons/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Lesson 1")

    def test_student_can_list_no_lessons(self):
        self.client.force_authenticate(user=self.student_user)
        response = self.client.get("/lessons/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_cannot_access(self):
        response = self.client.get("/lessons/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_lesson_as_teacher(self):
        self.client.force_authenticate(user=self.teacher_user)
        data = {
            "name": "New Lesson",
            "description": "New Desc",
            "section": self.section.id,
            "owner": self.teacher_user.id,
        }
        response = self.client.post("/lessons/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_admin_can_retrieve_lesson(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f"/lessons/{self.lesson1.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Lesson 1")

    def test_teacher_can_retrieve_own_lesson(self):
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.get(f"/lessons/{self.lesson1.pk}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teacher_cannot_retrieve_other_lesson(self):
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.get(f"/lessons/{self.lesson2.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_update_lesson(self):
        self.client.force_authenticate(user=self.admin_user)
        data = {
            "name": "Updated Lesson",
            "description": "Updated Desc",
            "section": self.section.id,
            "owner": self.admin_user.id,
        }
        response = self.client.put(f"/lessons/{self.lesson1.pk}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson1.refresh_from_db()
        self.assertEqual(self.lesson1.name, "Updated Lesson")

    def test_teacher_can_update_own_lesson(self):
        self.client.force_authenticate(user=self.teacher_user)
        data = {
            "name": "Updated by Teacher",
            "description": "Desc",
            "section": self.section.id,
            "owner": self.teacher_user.id,
        }
        response = self.client.put(f"/lessons/{self.lesson1.pk}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_teacher_cannot_update_other_lesson(self):
        self.client.force_authenticate(user=self.teacher_user)
        data = {
            "name": "Hacked",
            "description": "Desc",
            "section": self.section.id,
            "owner": self.teacher_user.id,
        }
        response = self.client.put(f"/lessons/{self.lesson2.pk}/", data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_delete_lesson(self):
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f"/lessons/{self.lesson1.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lesson.objects.filter(pk=self.lesson1.pk).exists())

    def test_teacher_can_delete_own_lesson(self):
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.delete(f"/lessons/{self.lesson1.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_teacher_cannot_delete_other_lesson(self):
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.delete(f"/lessons/{self.lesson2.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class GenericViewsTest(TestCase):
    def setUp(self):
        self.admin_group = Group.objects.create(name="Admin")
        self.teacher_group = Group.objects.create(name="Teacher")

        self.user = User.objects.create_user(email="user@example.com", password="pass")
        self.user.groups.add(self.teacher_group)

        self.section = Section.objects.create(
            name="Test Section", description="Desc", owner=self.user
        )
        self.lesson = Lesson.objects.create(
            name="Test Lesson",
            description="Desc",
            section=self.section,
            owner=self.user,
        )
        self.question = Question.objects.create(
            lesson=self.lesson, text="Test Question", order=1
        )
        self.correct_answer = Answer.objects.create(
            question=self.question, text="Correct", is_correct=True
        )
        self.wrong_answer = Answer.objects.create(
            question=self.question, text="Wrong", is_correct=False
        )

        self.client = Client()

    def test_profile_view_requires_login(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 302)

    def test_profile_view_logged_in(self):
        self.client.login(email="user@example.com", password="pass")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "home.html")
        self.assertIn("sections", response.context)

    def test_section_detail_view(self):
        response = self.client.get(f"/section/{self.section.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "section_detail.html")
        self.assertEqual(response.context["section"], self.section)

    def test_lesson_list_view(self):
        url = "/lesson/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertTemplateNotUsed(response, "lesson_list.html")
        self.assertNotIn("lesson_list", response.context)

    def test_lesson_detail_view(self):
        response = self.client.get(f"/lesson/{self.lesson.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "lesson_detail.html")
        self.assertEqual(response.context["lesson"], self.lesson)

    def test_lesson_test_view_get(self):
        response = self.client.get(f"/lessons/{self.lesson.pk}/test/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "lesson_test.html")
        self.assertIn("questions_with_answers", response.context)
        self.assertIsNone(response.context["results"])

    def test_lesson_test_view_post_correct_answer(self):
        self.client.login(email="user@example.com", password="pass")
        data = {f"answer_{self.question.id}": self.correct_answer.id}
        response = self.client.post(f"/lessons/{self.lesson.pk}/test/", data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.context)
        self.assertEqual(response.context["correct_count"], 1)
        self.assertEqual(response.context["total_questions"], 1)
        self.assertEqual(response.context["percentage"], 100.0)

    def test_lesson_test_view_post_wrong_answer(self):
        self.client.login(email="user@example.com", password="pass")
        data = {f"answer_{self.question.id}": self.wrong_answer.id}
        response = self.client.post(f"/lessons/{self.lesson.pk}/test/", data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["correct_count"], 0)
        self.assertEqual(response.context["percentage"], 0.0)

    def test_lesson_test_view_post_no_answer(self):
        self.client.login(email="user@example.com", password="pass")
        data = {}
        response = self.client.post(f"/lessons/{self.lesson.pk}/test/", data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["correct_count"], 0)
