import json

from django import forms
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.catalog.models import Question
from apps.catalog.selectors import (
    get_all_format_variants, get_chapters, get_format_variants,
    get_question, get_question_formats, get_questions, get_topics,
)
from apps.catalog.services import create_question, deactivate_question
from apps.teaching.forms.question import OptionFormSet, QuestionFilterForm, QuestionForm
from apps.teaching.views.common import owned_subject
from apps.accounts.decorators import partner_teacher_required
from core.utils.text import question_text_preview

PAGE_SIZE = 100


def _owned_question(request, pk):
    teacher = request.user.teacher
    question = get_question(pk)

    if question.topic.chapter.subject_id != teacher.subject_id or question.author_id != teacher.pk:
        raise Http404

    return question


def _question_panel_context(request, subject):
    teacher = request.user.teacher
    filter_form = QuestionFilterForm(request.GET, subject=subject)
    data = filter_form.cleaned_data if filter_form.is_valid() else {}

    questions = get_questions(
        subject=subject, author=teacher,
        grade_id=data['grade'].pk if data.get('grade') else None,
        chapter_id=data['chapter'].pk if data.get('chapter') else None,
        topic_id=data['topic'].pk if data.get('topic') else None,
        format_id=data['format'].pk if data.get('format') else None,
        variant_id=data['variant'].pk if data.get('variant') else None,
        search=data.get('q') or None,
    )

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
    format_codes = {str(f.id): f.code for f in get_question_formats()}
    variant_codes = {str(v.id): v.code for v in get_all_format_variants()}

    selected_format = form.instance.format if form.instance.pk else form.initial.get('format')
    selected_variant = form.instance.variant if form.instance.pk else form.initial.get('variant')
    if not selected_variant and selected_format:
        format_pk = getattr(selected_format, 'pk', None)
        if format_pk:
            selected_variant = get_format_variants(format_pk).first()

    return {
        'subject': subject,
        'form': form,
        'formset': formset,
        'media': form.media + formset.media,
        'tab': tab,
        'format_codes_json': json.dumps(format_codes),
        'variant_codes_json': json.dumps(variant_codes),
        'initial_format_code': selected_format.code if selected_format else '',
        'initial_variant_code': selected_variant.code if selected_variant else '',
        'variants_url': reverse('teaching:question-variant-field'),
        'topic_fields_url': reverse('teaching:question-topic-fields'),
    }


# Question
# ----------------------------------------------------------------------------------------------------------------------
# -------------- question list --------------
@partner_teacher_required
def question_list_view(request, pk):
    subject = owned_subject(request, pk)
    context = _question_panel_context(request, subject)

    if request.headers.get('HX-Request') == 'true':
        return render(request, 'teaching/subject/question/list/_panel.html', context)

    return render(request, 'teaching/subject/question/list/page.html', context)


# -------------- question create --------------
@partner_teacher_required
def question_create_view(request, pk):
    subject = owned_subject(request, pk)
    teacher = request.user.teacher

    if request.method == 'POST':
        form = QuestionForm(request.POST, subject=subject, teacher=teacher)
        formset = OptionFormSet(request.POST, instance=Question(), prefix='options')

        if form.is_valid() and formset.is_valid() and _validate_test_options(form, formset):
            options = [
                {'answer': f.cleaned_data['answer'], 'is_correct': f.cleaned_data.get('is_correct', False)}
                for f in formset.forms
                if f.cleaned_data and not f.cleaned_data.get('DELETE')
            ]
            create_question(
                topic=form.cleaned_data['topic'], author=teacher, text=form.cleaned_data['text'],
                format=form.cleaned_data['format'], variant=form.cleaned_data['variant'],
                level=form.cleaned_data['level'], time_limit=form.cleaned_data['time_limit'],
                options=options,
            )
            return redirect('teaching:question-list', subject.pk)
    else:
        first_format = get_question_formats().first()
        first_variant = get_format_variants(first_format.pk).first() if first_format else None
        initial = {'format': first_format, 'variant': first_variant}
        topic_id = request.GET.get('topic')
        if topic_id:
            initial['topic'] = topic_id

        form = QuestionForm(subject=subject, teacher=teacher, initial=initial)
        formset = OptionFormSet(instance=Question(), prefix='options')

    return render(
        request, 'teaching/subject/question/form/page.html',
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
            return redirect('teaching:question-list', subject.pk)
    else:
        form = QuestionForm(instance=question, subject=subject, teacher=teacher)
        formset = OptionFormSet(instance=question, prefix='options')

    context = _question_form_context(request, subject, form, formset, tab=request.GET.get('tab', 'question'))
    return render(request, 'teaching/subject/question/form/page.html', context)


# -------------- question delete --------------
@partner_teacher_required
def question_delete_view(request, pk):
    question = _owned_question(request, pk)
    subject = question.topic.chapter.subject

    deactivate_question(question)

    return render(
        request, 'teaching/subject/question/list/_panel.html',
        _question_panel_context(request, subject),
    )


# -------------- variant field (HTMX) --------------
@partner_teacher_required
def question_variant_field_view(request):
    format_id = request.GET.get('format')
    variants = get_format_variants(format_id)
    first_variant = variants.first()

    class _VariantForm(forms.Form):
        variant = forms.ModelChoiceField(
            queryset=variants,
            required=False, empty_label=_('No variant'),
        )

    field = _VariantForm(initial={'variant': first_variant})['variant']
    return render(request, 'teaching/subject/question/form/_variant_field.html', {
        'field': field,
        'initial_variant_code': first_variant.code if first_variant else '',
    })


# -------------- chapter + topic fields (HTMX) --------------
@partner_teacher_required
def question_topic_fields_view(request):
    subject_id = request.user.teacher.subject_id
    grade_id = request.GET.get('grade')
    chapter_id = request.GET.get('chapter')

    chapters = get_chapters(subject_id, grade_id=grade_id)
    topics = get_topics(subject_id, chapter_id=chapter_id, grade_id=grade_id)

    class _Form(forms.Form):
        chapter = forms.ModelChoiceField(queryset=chapters, required=False, empty_label=_('Select chapter'))
        topic = forms.ModelChoiceField(queryset=topics, required=False, empty_label=_('Select topic'))

    form = _Form(initial={'chapter': chapter_id})

    return render(request, 'teaching/subject/question/_topic_fields.html', {
        'chapter_field': form['chapter'],
        'topic_field': form['topic'],
        'topic_fields_url': reverse('teaching:question-topic-fields'),
    })
