from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, render
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from users.forms import CustomUserCreationForm
from users.serializers import UserSerializer

User = get_user_model()


class UserCreateAPIView(CreateAPIView):
    """
    Регистрация пользователя.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save(is_active=True)
        user.set_password(user.password)
        user.save()


def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Регистрация успешна! Теперь войдите.")
            return redirect("users:login")
    else:
        form = CustomUserCreationForm()
    return render(request, "register.html", {"form": form})
