from django import forms
from django.utils.translation import gettext_lazy as _
from core.forms.base import INPUT_CLASS, RichTextTextarea
from core.models import Chapter, Topic, Subject


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ('name', 'description', 'cover')
        widgets = {
            'name': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'description': RichTextTextarea(height='200px'),
            'cover': forms.FileInput(attrs={
                'class': 'hidden',
                'accept': 'image/*',
                'x-ref': 'coverInput',
                '@change': 'onChange($event)',
            }),
        }


class ChapterForm(forms.ModelForm):
    class Meta:
        model = Chapter
        fields = ('title', 'grade', 'description', 'order')
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'grade': forms.Select(attrs={'class': INPUT_CLASS}),
            'description': RichTextTextarea(height='160px'),
            'order': forms.NumberInput(attrs={'class': INPUT_CLASS}),
        }

    def __init__(self, *args, subject, **kwargs):
        super().__init__(*args, **kwargs)
        self.subject = subject

        self.fields['grade'].queryset = subject.grades.filter(is_active=True).order_by('order')
        self.fields['grade'].required = False
        self.fields['grade'].empty_label = _('General (all grades)')

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.subject = self.subject

        if commit:
            instance.save()

        return instance


class TopicForm(forms.ModelForm):
    class Meta:
        model = Topic
        fields = ('title', 'description', 'order')
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS}),
            'description': RichTextTextarea(height='160px'),
            'order': forms.NumberInput(attrs={'class': INPUT_CLASS}),
        }

    def __init__(self, *args, chapter, **kwargs):
        super().__init__(*args, **kwargs)
        self.chapter = chapter

    def clean_title(self):
        title = self.cleaned_data['title']
        qs = Topic.objects.filter(chapter=self.chapter, title=title, is_active=True)

        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError(_('A topic with this title already exists in this chapter.'))

        return title

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.chapter = self.chapter

        if commit:
            instance.save()

        return instance
