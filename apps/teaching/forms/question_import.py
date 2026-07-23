from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from core.forms.base import INPUT_CLASS, RichTextTextarea
from apps.catalog.models import Chapter, FormatVariant, Grade, Question, QuestionFormat, Topic
from apps.catalog.selectors import (
    get_chapters, get_format_variants_by_format_code, get_question_formats, get_subject_grades, get_topics,
)

DOCX_CONTENT_TYPES = (
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
)


class QuestionImportUploadForm(forms.Form):
    grade = forms.ModelChoiceField(queryset=Grade.objects.none(), required=False, empty_label=_('Select grade'))
    chapter = forms.ModelChoiceField(queryset=Chapter.objects.none(), required=False, empty_label=_('Select chapter'))
    topic = forms.ModelChoiceField(queryset=Topic.objects.none(), empty_label=_('Select topic'))
    format = forms.ModelChoiceField(queryset=QuestionFormat.objects.none(), empty_label=None)
    file = forms.FileField(label=_('Word file (.docx)'))

    def __init__(self, *args, subject, **kwargs):
        super().__init__(*args, **kwargs)

        grade_id = self.data.get('grade') if self.data else None
        chapter_id = self.data.get('chapter') if self.data else None

        self.fields['grade'].queryset = get_subject_grades(subject)
        self.fields['chapter'].queryset = get_chapters(subject, grade_id=grade_id)
        self.fields['topic'].queryset = get_topics(subject, chapter_id=chapter_id, grade_id=grade_id)
        self.fields['format'].queryset = get_question_formats()

    def clean_file(self):
        upload = self.cleaned_data['file']

        if not upload.name.lower().endswith('.docx'):
            raise forms.ValidationError(_('Please upload a .docx file.'))

        if upload.content_type not in DOCX_CONTENT_TYPES:
            raise forms.ValidationError(_('Please upload a .docx file.'))

        if upload.size > settings.QUESTION_IMPORT_MAX_FILE_SIZE:
            raise forms.ValidationError(_('The file is too large.'))

        return upload


class ImportedQuestionForm(forms.Form):
    include = forms.BooleanField(required=False, initial=True)
    text = forms.CharField(widget=RichTextTextarea(height='160px'))
    variant = forms.ModelChoiceField(queryset=FormatVariant.objects.none(), required=False)
    level = forms.ChoiceField(choices=Question.Level.choices, widget=forms.Select())
    time_limit = forms.IntegerField(min_value=5, initial=30, widget=forms.NumberInput(attrs={'class': INPUT_CLASS}))

    def __init__(self, *args, format_code, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['variant'].queryset = get_format_variants_by_format_code(format_code)


class ImportedOptionForm(forms.Form):
    text = forms.CharField(widget=RichTextTextarea(height='100px'))
    is_correct = forms.BooleanField(required=False)


ImportedOptionFormSet = forms.formset_factory(ImportedOptionForm, extra=0, can_delete=True)


class ImportedMatchPairForm(forms.Form):
    left = forms.CharField(widget=RichTextTextarea(height='100px'))
    right = forms.CharField(widget=RichTextTextarea(height='100px'))


ImportedMatchPairFormSet = forms.formset_factory(ImportedMatchPairForm, extra=0, can_delete=True)
