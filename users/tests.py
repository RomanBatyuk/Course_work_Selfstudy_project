from django.contrib import messages
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from users.forms import CustomUserCreationForm

User = get_user_model()


# Тесты для register_view (обычный Django view)
class RegisterViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Используем reverse с namespace 'users' для view (на основе редиректа в ошибке)
        self.url = reverse("users:register")  # Путь: /users/register/

    def test_register_view_get(self):
        """Тест GET-запроса для страницы регистрации (рендеринг формы)."""
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")  # Замените на ваш шаблон
        self.assertIsInstance(response.context["form"], CustomUserCreationForm)

    def test_register_view_post_valid(self):
        """Тест POST-запроса с валидными данными формы."""
        data = {
            "email": "new@example.com",
            "password1": "strongpass123",
            "password2": "strongpass123",
        }
        response = self.client.post(self.url, data)

        # Редирект на login с namespace 'users' (на основе фактического редиректа)
        self.assertRedirects(response, reverse("users:login"))  # Путь: /users/login/

        user = User.objects.get(email="new@example.com")
        self.assertEqual(user.email, "new@example.com")

        messages_list = [
            msg.message for msg in messages.get_messages(response.wsgi_request)
        ]
        self.assertIn(
            "Регистрация успешна! Теперь войдите.", messages_list
        )  # Адаптируйте сообщение

    def test_register_view_post_invalid(self):
        """Тест POST-запроса с невалидными данными формы."""
        data = {"email": "invalid-email", "password1": "123", "password2": "456"}
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")

        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)
        self.assertIn("password2", form.errors)

        self.assertFalse(User.objects.filter(email="invalid-email").exists())

    def test_register_view_post_duplicate_email(self):
        """Тест POST-запроса с существующим email."""
        User.objects.create_user(email="existing@example.com", password="pass123")

        data = {
            "email": "existing@example.com",
            "password1": "newpass123",
            "password2": "newpass123",
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")

        form = response.context["form"]
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

        self.assertEqual(User.objects.filter(email="existing@example.com").count(), 1)
