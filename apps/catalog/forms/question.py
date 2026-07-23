from django import forms
from django.urls import reverse_lazy
from unfold.widgets import UnfoldAdminSelectWidget
from apps.catalog.models import Question, Option, MatchPair
from core.forms.base import RichTextTextarea


# QuestionAdminForm
class QuestionAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'
        widgets = {
            'text': RichTextTextarea(height='250px'),
            'format': UnfoldAdminSelectWidget(attrs={
                'data-variants-url': reverse_lazy('catalog:format-variants'),
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


# MatchPairAdminForm
class MatchPairAdminForm(forms.ModelForm):
    class Meta:
        model = MatchPair
        fields = '__all__'
        widgets = {
            'left': RichTextTextarea(height='120px'),
            'right': RichTextTextarea(height='120px'),
        }
