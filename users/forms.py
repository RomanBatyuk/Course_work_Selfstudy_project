from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Введите email"}
        ),
    )

    class Meta:
        model = User
        fields = (
            "email",
            "password1",
            "password2",
        )  # Убрали 'username' — теперь только email и пароли

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data[
            "email"
        ]  # Необязательно, но для явности (Django сам установит из USERNAME_FIELD)
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Убираем username из полей формы, если он там появился (хотя в Meta его нет)
        if "username" in self.fields:
            del self.fields["username"]
        # Стилизация
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
