from django import forms

from materials.models import Lesson, Section


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ["name", "description"]  # owner зададим в view
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Название раздела"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Описание раздела",
                    "rows": 3,
                }
            ),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ["section", "name", "description"]  # section выберет пользователь
        widgets = {
            "section": forms.Select(attrs={"class": "form-control"}),
            "name": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Название урока"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Описание урока",
                    "rows": 3,
                }
            ),
        }
