from django import forms
from core.models import Question
from core.forms.base import RichTextTextarea


class QuestionAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'
        widgets = {
            'text': RichTextTextarea(),
        }
