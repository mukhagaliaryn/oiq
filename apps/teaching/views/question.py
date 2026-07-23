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
    get_question, get_question_formats, get_question_stats, get_questions, get_topics,
)
from apps.catalog.services import create_question, deactivate_question
from apps.teaching.forms.question import MatchPairFormSet, OptionFormSet, QuestionFilterForm, QuestionForm
from apps.teaching.views.common import owned_subject
from apps.accounts.decorators import partner_teacher_required
from core.utils.text import question_text_preview

PAGE_SIZE = 100


def _owned_question(request, pk):
    teacher = request.user.teacher
    question = get_question(pk)

    if not teacher.subjects.filter(pk=question.topic.chapter.subject_id).exists():
        raise Http404

    return question


def _question_panel_context(request, subject):
    filter_form = QuestionFilterForm(request.GET, subject=subject)
    data = filter_form.cleaned_data if filter_form.is_valid() else {}

    questions = get_questions(
        subject=subject,
        author=data.get('author'),
        grade_id=data['grade'].pk if data.get('grade') else None,
        chapter_id=data['chapter'].pk if data.get('chapter') else None,
        topic_id=data['topic'].pk if data.get('topic') else None,
        format_id=data['format'].pk if data.get('format') else None,
        variant_id=data['variant'].pk if data.get('variant') else None,
        search=data.get('q') or None,
    )

    stats = get_question_stats(questions)
    page_obj = Paginator(questions, PAGE_SIZE).get_page(request.GET.get('page'))

    for question in page_obj:
        question.text_preview = question_text_preview(question.text)

    return {
        'subject': subject,
        'filter_form': filter_form,
        'page_obj': page_obj,
        'stats': stats,
    }


def _validate_test_options(formset):
    surviving = [f for f in formset.forms if f.cleaned_data and not f.cleaned_data.get('DELETE')]

    if len(surviving) >= 2 and any(f.cleaned_data.get('is_correct') for f in surviving):
        return True

    formset._non_form_errors = formset.error_class([
        _('Add at least two options and mark one of them as correct.'),
    ])
    return False


def _validate_match_pairs(formset):
    surviving = [f for f in formset.forms if f.cleaned_data and not f.cleaned_data.get('DELETE')]

    if len(surviving) >= 2:
        return True

    formset._non_form_errors = formset.error_class([
        _('Add at least two match pairs.'),
    ])
    return False


def _validate_answer_data(format_code, option_formset, match_pair_formset):
    if format_code == 'test':
        return _validate_test_options(option_formset)

    if format_code == 'matching':
        return _validate_match_pairs(match_pair_formset)

    return True


def _question_form_context(request, subject, form, option_formset, match_pair_formset, tab='question'):
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
        'option_formset': option_formset,
        'match_pair_formset': match_pair_formset,
        'media': form.media + option_formset.media + match_pair_formset.media,
        'tab': tab,
        'format_codes_json': json.dumps(format_codes),
        'variant_codes_json': json.dumps(variant_codes),
        'initial_format_code': selected_format.code if selected_format else '',
        'initial_variant_code': selected_variant.code if selected_variant else '',
        'variants_url': reverse('teaching:question-variant-field'),
        'topic_fields_url': f"{reverse('teaching:question-topic-fields')}?subject={subject.pk}",
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
        option_formset = OptionFormSet(request.POST, instance=Question(), prefix='options')
        match_pair_formset = MatchPairFormSet(request.POST, instance=Question(), prefix='pairs')

        if form.is_valid() and option_formset.is_valid() and match_pair_formset.is_valid():
            format_code = form.cleaned_data['format'].code

            if _validate_answer_data(format_code, option_formset, match_pair_formset):
                options = None
                match_pairs = None

                if format_code == 'test':
                    options = [
                        {'answer': f.cleaned_data['answer'], 'is_correct': f.cleaned_data.get('is_correct', False)}
                        for f in option_formset.forms
                        if f.cleaned_data and not f.cleaned_data.get('DELETE')
                    ]
                elif format_code == 'matching':
                    match_pairs = [
                        {'left': f.cleaned_data['left'], 'right': f.cleaned_data['right']}
                        for f in match_pair_formset.forms
                        if f.cleaned_data and not f.cleaned_data.get('DELETE')
                    ]

                create_question(
                    topic=form.cleaned_data['topic'], author=teacher, text=form.cleaned_data['text'],
                    format=form.cleaned_data['format'], variant=form.cleaned_data['variant'],
                    level=form.cleaned_data['level'], time_limit=form.cleaned_data['time_limit'],
                    options=options, match_pairs=match_pairs,
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
        option_formset = OptionFormSet(instance=Question(), prefix='options')
        match_pair_formset = MatchPairFormSet(instance=Question(), prefix='pairs')

    return render(
        request, 'teaching/subject/question/form/page.html',
        _question_form_context(request, subject, form, option_formset, match_pair_formset),
    )


# -------------- question update --------------
@partner_teacher_required
def question_update_view(request, pk):
    question = _owned_question(request, pk)
    subject = question.topic.chapter.subject
    teacher = request.user.teacher

    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question, subject=subject, teacher=teacher)
        option_formset = OptionFormSet(request.POST, instance=question, prefix='options')
        match_pair_formset = MatchPairFormSet(request.POST, instance=question, prefix='pairs')

        if form.is_valid() and option_formset.is_valid() and match_pair_formset.is_valid():
            format_code = form.cleaned_data['format'].code

            if _validate_answer_data(format_code, option_formset, match_pair_formset):
                form.save()

                if format_code == 'test':
                    option_formset.save()
                elif format_code == 'matching':
                    match_pair_formset.save()

                return redirect('teaching:question-list', subject.pk)
    else:
        form = QuestionForm(instance=question, subject=subject, teacher=teacher)
        option_formset = OptionFormSet(instance=question, prefix='options')
        match_pair_formset = MatchPairFormSet(instance=question, prefix='pairs')

    context = _question_form_context(
        request, subject, form, option_formset, match_pair_formset, tab=request.GET.get('tab', 'question'),
    )
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
    teacher = request.user.teacher
    subject_id = request.GET.get('subject')
    grade_id = request.GET.get('grade')
    chapter_id = request.GET.get('chapter')

    if not subject_id or not teacher.subjects.filter(pk=subject_id).exists():
        raise Http404

    chapters = get_chapters(subject_id, grade_id=grade_id)
    topics = get_topics(subject_id, chapter_id=chapter_id, grade_id=grade_id)

    class _Form(forms.Form):
        chapter = forms.ModelChoiceField(queryset=chapters, required=False, empty_label=_('Select chapter'))
        topic = forms.ModelChoiceField(queryset=topics, required=False, empty_label=_('Select topic'))

    form = _Form(initial={'chapter': chapter_id})

    return render(request, 'teaching/subject/question/_topic_fields.html', {
        'chapter_field': form['chapter'],
        'topic_field': form['topic'],
        'topic_fields_url': f"{reverse('teaching:question-topic-fields')}?subject={subject_id}",
    })
