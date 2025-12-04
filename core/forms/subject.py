from ckeditor.widgets import CKEditorWidget
from django import forms
from core.models import Question, Option


# Question
# ----------------------------------------------------------------------------------------------------------------------
# QuestionForm
class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'
        widgets = {
            'body': CKEditorWidget(config_name='default'),
        }


# Question variants
# ----------------------------------------------------------------------------------------------------------------------
# OptionForm
class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = '__all__'
        widgets = {
            'answer': CKEditorWidget(config_name='default'),
        }
