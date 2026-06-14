from django import forms
from core.models import Question, Option
from core.forms.base import RichTextTextarea


# QuestionAdminForm
class QuestionAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'
        widgets = {
            'text': RichTextTextarea(height='250px'),
        }


# OptionAdminForm
class OptionAdminForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = '__all__'
        widgets = {
            'answer': RichTextTextarea(height='180px'),
        }
