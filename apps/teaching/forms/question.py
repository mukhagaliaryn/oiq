from django import forms
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _
from core.forms.base import INPUT_CLASS, RichTextTextarea
from apps.catalog.models import Chapter, FormatVariant, Option, Question, QuestionFormat, Topic
from apps.catalog.selectors import get_chapters, get_format_variants, get_question_formats, get_subject_grades, get_topics
from apps.directory.models import Grade


class QuestionFilterForm(forms.Form):
    grade = forms.ModelChoiceField(queryset=Grade.objects.none(), required=False, empty_label=_('All grades'))
    chapter = forms.ModelChoiceField(queryset=Chapter.objects.none(), required=False, empty_label=_('All chapters'))
    topic = forms.ModelChoiceField(queryset=Topic.objects.none(), required=False, empty_label=_('All topics'))
    format = forms.ModelChoiceField(queryset=QuestionFormat.objects.none(), required=False, empty_label=_('All formats'))
    variant = forms.ModelChoiceField(queryset=FormatVariant.objects.none(), required=False, empty_label=_('All variants'))
    q = forms.CharField(required=False, label=_('Search'), widget=forms.TextInput(attrs={'class': INPUT_CLASS}))

    def __init__(self, *args, subject, **kwargs):
        super().__init__(*args, **kwargs)

        grade_id = self.data.get('grade')
        chapter_id = self.data.get('chapter')
        format_id = self.data.get('format')

        self.fields['grade'].queryset = get_subject_grades(subject)
        self.fields['chapter'].queryset = get_chapters(subject, grade_id=grade_id)
        self.fields['topic'].queryset = get_topics(subject, chapter_id=chapter_id, grade_id=grade_id)
        self.fields['format'].queryset = get_question_formats()
        self.fields['variant'].queryset = get_format_variants(format_id)


class QuestionForm(forms.ModelForm):
    grade = forms.ModelChoiceField(queryset=Grade.objects.none(), required=False, empty_label=_('Select grade'))
    chapter = forms.ModelChoiceField(queryset=Chapter.objects.none(), required=False, empty_label=_('Select chapter'))

    class Meta:
        model = Question
        fields = ('topic', 'text', 'format', 'variant', 'level', 'time_limit')
        widgets = {
            'text': RichTextTextarea(height='220px'),
            'time_limit': forms.NumberInput(attrs={'class': INPUT_CLASS}),
        }

    def __init__(self, *args, subject, teacher, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher = teacher

        if self.instance.pk and self.instance.topic_id and 'grade' not in self.initial:
            self.initial['grade'] = self.instance.topic.chapter.grade_id
            self.initial['chapter'] = self.instance.topic.chapter_id

        self.fields['grade'].queryset = get_subject_grades(subject)

        grade_id = self._field_value('grade')
        chapter_id = self._field_value('chapter')

        self.fields['chapter'].queryset = get_chapters(subject, grade_id=grade_id)
        self.fields['topic'].queryset = get_topics(subject, chapter_id=chapter_id, grade_id=grade_id)

        self.fields['format'].queryset = get_question_formats()
        self.fields['format'].empty_label = None

        format_id = self._field_value('format')
        self.fields['variant'].queryset = get_format_variants(format_id)
        self.fields['variant'].required = False
        self.fields['variant'].empty_label = _('No variant')

        if self.instance.pk:
            self.fields['format'].disabled = True

    def _field_value(self, name):
        raw = self.data.get(self.add_prefix(name))
        if raw:
            return raw

        initial = self.initial.get(name)
        return getattr(initial, 'pk', initial)

    def save(self, commit=True):
        instance = super().save(commit=False)

        if not instance.pk:
            instance.author = self.teacher

        if commit:
            instance.save()

        return instance


class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ('answer', 'is_correct')
        widgets = {
            'answer': RichTextTextarea(height='100px'),
        }


OptionFormSet = inlineformset_factory(
    Question, Option, form=OptionForm,
    extra=0, can_delete=True, validate_min=False,
)
