import json

from django import forms
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.dashboard.teacher.forms.question import OptionFormSet, QuestionFilterForm, QuestionForm, _topic_label
from apps.dashboard.teacher.views.common import owned_subject
from core.models import Chapter, FormatVariant, Question, QuestionFormat, Topic
from core.utils.decorators import partner_teacher_required
from core.utils.text import question_text_preview

PAGE_SIZE = 100


def _owned_question(request, pk):
    teacher = request.user.teacher
    return get_object_or_404(
        Question.objects.filter(topic__chapter__subject_id=teacher.subject_id, author=teacher, is_active=True),
        pk=pk,
    )


def _question_panel_context(request, subject):
    teacher = request.user.teacher
    filter_form = QuestionFilterForm(request.GET, subject=subject)
    data = filter_form.cleaned_data if filter_form.is_valid() else {}

    questions = (
        Question.objects.filter(topic__chapter__subject=subject, author=teacher, is_active=True)
        .select_related('topic', 'topic__chapter', 'format', 'variant')
        .order_by('-created_at')
    )

    if data.get('grade'):
        questions = questions.filter(topic__chapter__grade=data['grade'])
    if data.get('chapter'):
        questions = questions.filter(topic__chapter=data['chapter'])
    if data.get('topic'):
        questions = questions.filter(topic=data['topic'])
    if data.get('format'):
        questions = questions.filter(format=data['format'])
    if data.get('variant'):
        questions = questions.filter(variant=data['variant'])
    if data.get('q'):
        questions = questions.filter(text__icontains=data['q'])

    page_obj = Paginator(questions, PAGE_SIZE).get_page(request.GET.get('page'))

    for question in page_obj:
        question.text_preview = question_text_preview(question.text)

    return {
        'subject': subject,
        'filter_form': filter_form,
        'page_obj': page_obj,
    }


def _validate_test_options(form, formset):
    if not form.cleaned_data.get('format') or form.cleaned_data['format'].code != 'test':
        return True

    surviving = [f for f in formset.forms if f.cleaned_data and not f.cleaned_data.get('DELETE')]

    if len(surviving) >= 2 and any(f.cleaned_data.get('is_correct') for f in surviving):
        return True

    formset._non_form_errors = formset.error_class([
        _('Add at least two options and mark one of them as correct.'),
    ])
    return False


def _question_form_context(request, subject, form, formset, tab='question'):
    format_codes = {str(f.id): f.code for f in QuestionFormat.objects.order_by('order')}
    selected_format = form.instance.format if form.instance.pk else form.initial.get('format')

    return {
        'subject': subject,
        'form': form,
        'formset': formset,
        'media': form.media + formset.media,
        'tab': tab,
        'format_codes_json': json.dumps(format_codes),
        'initial_format_code': selected_format.code if selected_format else '',
        'variants_url': reverse('teacher:question-variant-field'),
        'topic_fields_url': reverse('teacher:question-topic-fields'),
    }


# Question
# ----------------------------------------------------------------------------------------------------------------------
# -------------- question list --------------
@partner_teacher_required
def question_list_view(request, pk):
    subject = owned_subject(request, pk)
    context = _question_panel_context(request, subject)

    if request.headers.get('HX-Request') == 'true':
        return render(request, 'app/dashboard/teacher/subject/question/_panel.html', context)

    return render(request, 'app/dashboard/teacher/subject/question/list.html', context)


# -------------- question create --------------
@partner_teacher_required
def question_create_view(request, pk):
    subject = owned_subject(request, pk)
    teacher = request.user.teacher

    if request.method == 'POST':
        form = QuestionForm(request.POST, subject=subject, teacher=teacher)
        formset = OptionFormSet(request.POST, instance=Question(), prefix='options')

        if form.is_valid() and formset.is_valid() and _validate_test_options(form, formset):
            question = form.save()
            formset.instance = question
            formset.save()
            return redirect('teacher:question-list', subject.pk)
    else:
        initial = {'format': QuestionFormat.objects.order_by('order').first()}
        topic_id = request.GET.get('topic')
        if topic_id:
            initial['topic'] = topic_id

        form = QuestionForm(subject=subject, teacher=teacher, initial=initial)
        formset = OptionFormSet(instance=Question(), prefix='options')

    return render(
        request, 'app/dashboard/teacher/subject/question/form.html',
        _question_form_context(request, subject, form, formset),
    )


# -------------- question update --------------
@partner_teacher_required
def question_update_view(request, pk):
    question = _owned_question(request, pk)
    subject = question.topic.chapter.subject
    teacher = request.user.teacher

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question, subject=subject, teacher=teacher)
        formset = OptionFormSet(request.POST, instance=question, prefix='options')

        if form.is_valid() and formset.is_valid() and _validate_test_options(form, formset):
            form.save()
            formset.save()
            return redirect('teacher:question-list', subject.pk)
    else:
        form = QuestionForm(instance=question, subject=subject, teacher=teacher)
        formset = OptionFormSet(instance=question, prefix='options')

    context = _question_form_context(request, subject, form, formset, tab=request.GET.get('tab', 'question'))
    return render(request, 'app/dashboard/teacher/subject/question/form.html', context)


# -------------- question delete --------------
@partner_teacher_required
def question_delete_view(request, pk):
    question = _owned_question(request, pk)
    subject = question.topic.chapter.subject

    question.is_active = False
    question.save(update_fields=['is_active'])

    return render(
        request, 'app/dashboard/teacher/subject/question/_panel.html',
        _question_panel_context(request, subject),
    )


# -------------- variant field (HTMX) --------------
@partner_teacher_required
def question_variant_field_view(request):
    class _VariantForm(forms.Form):
        variant = forms.ModelChoiceField(
            queryset=FormatVariant.objects.filter(format_id=request.GET.get('format')).order_by('order'),
            required=False, empty_label=_('No variant'),
        )

    field = _VariantForm()['variant']
    return render(request, 'app/dashboard/teacher/subject/question/_variant_field.html', {'field': field})


# -------------- chapter + topic fields (HTMX) --------------
@partner_teacher_required
def question_topic_fields_view(request):
    subject_id = request.user.teacher.subject_id
    grade_id = request.GET.get('grade')
    chapter_id = request.GET.get('chapter')

    chapters = Chapter.objects.filter(subject_id=subject_id, is_active=True)
    if grade_id:
        chapters = chapters.filter(Q(grade_id=grade_id) | Q(grade__isnull=True))
    chapters = chapters.order_by('order')

    topics = Topic.objects.filter(chapter__subject_id=subject_id, is_active=True).select_related('chapter')
    if chapter_id:
        topics = topics.filter(chapter_id=chapter_id)
    elif grade_id:
        topics = topics.filter(Q(chapter__grade_id=grade_id) | Q(chapter__grade__isnull=True))
    topics = topics.order_by('chapter__order', 'order')

    class _Form(forms.Form):
        chapter = forms.ModelChoiceField(queryset=chapters, required=False, empty_label=_('Select chapter'))
        topic = forms.ModelChoiceField(queryset=topics, required=False, empty_label=_('Select topic'))

    form = _Form(initial={'chapter': chapter_id})
    form.fields['topic'].label_from_instance = _topic_label

    return render(request, 'app/dashboard/teacher/subject/question/_topic_fields.html', {
        'chapter_field': form['chapter'],
        'topic_field': form['topic'],
        'topic_fields_url': reverse('teacher:question-topic-fields'),
    })
