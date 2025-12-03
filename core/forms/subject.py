from ckeditor.widgets import CKEditorWidget
from django import forms
from core.models import Question


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = '__all__'
        widgets = {
            'body': CKEditorWidget(config_name='default'),
        }

    def __init__(self, *args, **kwargs):
        request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        if request is not None:
            lang = (request.LANGUAGE_CODE or 'en').split('-')[0]
            self.fields['body'].widget.config['language'] = lang
