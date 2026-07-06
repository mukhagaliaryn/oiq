from django import forms
from django.conf import settings
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from core.forms.base import INPUT_CLASS, RichTextTextarea
from core.models import Chapter, FormatVariant, Grade, Question, Topic

DOCX_CONTENT_TYPES = (
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
)


class QuestionImportUploadForm(forms.Form):
    grade = forms.ModelChoiceField(queryset=Grade.objects.none(), required=False, empty_label=_('Select grade'))
    chapter = forms.ModelChoiceField(queryset=Chapter.objects.none(), required=False, empty_label=_('Select chapter'))
    topic = forms.ModelChoiceField(queryset=Topic.objects.none(), empty_label=_('Select topic'))
    file = forms.FileField(label=_('Word file (.docx)'))

    def __init__(self, *args, subject, **kwargs):
        super().__init__(*args, **kwargs)

        grade_id = self.data.get('grade') if self.data else None
        chapter_id = self.data.get('chapter') if self.data else None

        self.fields['grade'].queryset = subject.grades.filter(is_active=True).order_by('order')

        chapters = Chapter.objects.filter(subject=subject, is_active=True)
        if grade_id:
            chapters = chapters.filter(Q(grade_id=grade_id) | Q(grade__isnull=True))
        self.fields['chapter'].queryset = chapters.order_by('order')

        topics = Topic.objects.filter(chapter__subject=subject, is_active=True).select_related('chapter')
        if chapter_id:
            topics = topics.filter(chapter_id=chapter_id)
        elif grade_id:
            topics = topics.filter(Q(chapter__grade_id=grade_id) | Q(chapter__grade__isnull=True))
        self.fields['topic'].queryset = topics.order_by('chapter__order', 'order')

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
    variant = forms.ModelChoiceField(queryset=FormatVariant.objects.filter(format__code='test').order_by('order'))
    level = forms.ChoiceField(choices=Question.Level.choices, widget=forms.Select())
    time_limit = forms.IntegerField(min_value=5, initial=30, widget=forms.NumberInput(attrs={'class': INPUT_CLASS}))


class ImportedOptionForm(forms.Form):
    text = forms.CharField(widget=RichTextTextarea(height='100px'))
    is_correct = forms.BooleanField(required=False)


ImportedOptionFormSet = forms.formset_factory(ImportedOptionForm, extra=0, can_delete=True)
