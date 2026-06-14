from django import forms
from django.urls import reverse_lazy
from unfold.widgets import UnfoldAdminSelectWidget
from core.models import Question, Option
from core.forms.base import RichTextTextarea


# QuestionAdminForm
class QuestionAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'
        widgets = {
            'text': RichTextTextarea(height='250px'),
            'format': UnfoldAdminSelectWidget(attrs={
                'data-variants-url': reverse_lazy('core:format-variants'),
            }),
        }


# OptionAdminForm
class OptionAdminForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = '__all__'
        widgets = {
            'answer': RichTextTextarea(height='180px'),
        }
