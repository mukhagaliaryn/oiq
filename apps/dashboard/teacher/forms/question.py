from django import forms
from django.db.models import Q
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from core.forms.base import INPUT_CLASS, RichTextTextarea
from core.models import Chapter, FormatVariant, Grade, Option, Question, QuestionFormat, Topic


def _topic_label(topic):
    return f'{topic.chapter.title} — {topic.title}'


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
        self.fields['topic'].label_from_instance = _topic_label

        self.fields['format'].queryset = QuestionFormat.objects.order_by('order')
        self.fields['variant'].queryset = (
            FormatVariant.objects.filter(format_id=format_id).order_by('order')
            if format_id else FormatVariant.objects.none()
        )


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

        self.fields['grade'].queryset = subject.grades.filter(is_active=True).order_by('order')

        grade_id = self._field_value('grade')
        chapters = Chapter.objects.filter(subject=subject, is_active=True)
        if grade_id:
            chapters = chapters.filter(Q(grade_id=grade_id) | Q(grade__isnull=True))
        self.fields['chapter'].queryset = chapters.order_by('order')

        chapter_id = self._field_value('chapter')
        topics = Topic.objects.filter(chapter__subject=subject, is_active=True).select_related('chapter')
        if chapter_id:
            topics = topics.filter(chapter_id=chapter_id)
        elif grade_id:
            topics = topics.filter(Q(chapter__grade_id=grade_id) | Q(chapter__grade__isnull=True))
        self.fields['topic'].queryset = topics.order_by('chapter__order', 'order')
        self.fields['topic'].label_from_instance = _topic_label

        self.fields['format'].queryset = QuestionFormat.objects.order_by('order')
        self.fields['format'].empty_label = None

        format_id = self._field_value('format')
        self.fields['variant'].queryset = (
            FormatVariant.objects.filter(format_id=format_id).order_by('order') if format_id else FormatVariant.objects.none()
        )
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
            'is_correct': forms.CheckboxInput(attrs={
                'class': 'size-5 rounded border-default accent-brand focus:ring-2 focus:ring-brand',
            }),
        }


OptionFormSet = inlineformset_factory(
    Question, Option, form=OptionForm,
    extra=1, can_delete=True, validate_min=False,
)
