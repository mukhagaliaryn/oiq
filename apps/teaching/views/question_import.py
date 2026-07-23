import json
import uuid
from dataclasses import asdict

from django.contrib import messages
from django.core.files.storage import default_storage
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from apps.catalog.selectors import get_format_variants_by_format_code, get_question_format, get_topic
from apps.catalog.services import create_question
from apps.teaching.forms.question_import import (
    ImportedMatchPairFormSet, ImportedOptionFormSet, ImportedQuestionForm, QuestionImportUploadForm,
)
from apps.teaching.services.question_import import (
    ParsedOption, ParsedPair, ParsedQuestion, QuestionImportError, run_question_import,
)
from apps.teaching.views.common import owned_subject
from apps.accounts.decorators import partner_teacher_required

SESSION_KEY_PREFIX = 'question_import'


def _session_key(import_id):
    return f'{SESSION_KEY_PREFIX}:{import_id}'


def _owned_topic(subject, topic_id):
    topic = get_topic(topic_id)

    if topic.chapter.subject_id != subject.pk:
        raise Http404

    return topic


def _parsed_question_from_dict(data):
    return ParsedQuestion(**{
        **data,
        'options': [ParsedOption(**option) for option in data['options']],
        'pairs': [ParsedPair(**pair) for pair in data['pairs']],
    })


def _variant_codes_json(format_code):
    if format_code != 'test':
        return json.dumps({})

    return json.dumps({str(variant.id): variant.code for variant in get_format_variants_by_format_code('test')})


def _question_forms_from_parsed(questions, format_code):
    items = []
    for index, question in enumerate(questions):
        prefix = f'q{index}'
        variant = None
        if format_code == 'test':
            variant = get_format_variants_by_format_code('test').filter(code=question.variant_code).first()

        question_form = ImportedQuestionForm(prefix=prefix, format_code=format_code, initial={
            'include': True,
            'text': question.text_html,
            'variant': variant.pk if variant else None,
            'level': question.level,
            'time_limit': 30,
        })
        option_formset = ImportedOptionFormSet(prefix=f'{prefix}-options', initial=[
            {'text': option.text_html, 'is_correct': option.is_correct}
            for option in question.options
        ] if format_code == 'test' else [])
        pair_formset = ImportedMatchPairFormSet(prefix=f'{prefix}-pairs', initial=[
            {'left': pair.left_html, 'right': pair.right_html}
            for pair in question.pairs
        ] if format_code == 'matching' else [])

        items.append({
            'index': index, 'question_form': question_form,
            'option_formset': option_formset, 'pair_formset': pair_formset,
            'warning': question.warning,
        })

    return items


def _question_forms_from_post(post_data, count, format_code):
    items = []
    for index in range(count):
        prefix = f'q{index}'
        question_form = ImportedQuestionForm(post_data, prefix=prefix, format_code=format_code)
        option_formset = ImportedOptionFormSet(post_data, prefix=f'{prefix}-options')
        pair_formset = ImportedMatchPairFormSet(post_data, prefix=f'{prefix}-pairs')

        items.append({
            'index': index, 'question_form': question_form,
            'option_formset': option_formset, 'pair_formset': pair_formset,
            'warning': '',
        })

    return items


def _validate_option_rules(question_form, option_formset):
    surviving = [f for f in option_formset.forms if f.cleaned_data and not f.cleaned_data.get('DELETE')]
    correct_count = sum(1 for f in surviving if f.cleaned_data.get('is_correct'))

    if len(surviving) < 2:
        option_formset._non_form_errors = option_formset.error_class([_('Add at least two options.')])
        return False

    variant = question_form.cleaned_data['variant']
    if variant.code == 'single' and correct_count != 1:
        option_formset._non_form_errors = option_formset.error_class([_('Mark exactly one option as correct.')])
        return False

    if variant.code == 'multiple' and correct_count < 1:
        option_formset._non_form_errors = option_formset.error_class([_('Mark at least one option as correct.')])
        return False

    return True


def _validate_pair_rules(pair_formset):
    surviving = [f for f in pair_formset.forms if f.cleaned_data and not f.cleaned_data.get('DELETE')]

    if len(surviving) < 2:
        pair_formset._non_form_errors = pair_formset.error_class([_('Add at least two match pairs.')])
        return False

    return True


def _validate_answer_data(format_code, question_form, option_formset, pair_formset):
    if not question_form.cleaned_data.get('include'):
        return True

    if format_code == 'test':
        return _validate_option_rules(question_form, option_formset)

    if format_code == 'matching':
        return _validate_pair_rules(pair_formset)

    return True


# Question import (AI, .docx)
# ----------------------------------------------------------------------------------------------------------------------
# -------------- upload + parse --------------
@partner_teacher_required
def question_import_view(request, pk):
    subject = owned_subject(request, pk)

    if request.method == 'POST':
        upload_form = QuestionImportUploadForm(request.POST, request.FILES, subject=subject)

        if upload_form.is_valid():
            import_id = uuid.uuid4().hex
            question_format = upload_form.cleaned_data['format']

            try:
                result = run_question_import(upload_form.cleaned_data['file'].read(), import_id, question_format.code)
            except QuestionImportError as error:
                messages.error(request, str(error))
                return render(request, 'teaching/subject/question/import/page.html', {
                    'subject': subject, 'upload_form': upload_form,
                    'topic_fields_url': f"{reverse('teaching:question-topic-fields')}?subject={subject.pk}",
                })

            supported = [q for q in result.questions if q.is_supported_for(question_format.code)]
            unsupported = [q for q in result.questions if not q.is_supported_for(question_format.code)]

            if not supported:
                for path in result.image_paths:
                    default_storage.delete(path)

                messages.error(request, _('No importable questions were found in this file.'))
                return render(request, 'teaching/subject/question/import/page.html', {
                    'subject': subject, 'upload_form': upload_form,
                    'topic_fields_url': f"{reverse('teaching:question-topic-fields')}?subject={subject.pk}",
                })

            request.session[_session_key(import_id)] = {
                'topic_id': upload_form.cleaned_data['topic'].pk,
                'format_id': question_format.pk,
                'questions': [asdict(question) for question in supported],
                'unsupported': [asdict(question) for question in unsupported],
                'image_paths': result.image_paths,
            }

            return redirect('teaching:question-import-review', subject.pk, import_id)
    else:
        upload_form = QuestionImportUploadForm(subject=subject)

    return render(request, 'teaching/subject/question/import/page.html', {
        'subject': subject, 'upload_form': upload_form,
        'topic_fields_url': f"{reverse('teaching:question-topic-fields')}?subject={subject.pk}",
    })


# -------------- review (GET, reloadable — no AI call) --------------
@partner_teacher_required
def question_import_review_view(request, pk, import_id):
    subject = owned_subject(request, pk)
    data = request.session.get(_session_key(import_id))

    if not data:
        messages.error(request, _('This import session has expired or was already completed. Please upload the file again.'))
        return redirect('teaching:question-import', subject.pk)

    topic = _owned_topic(subject, data['topic_id'])
    question_format = get_question_format(data['format_id'])
    questions = [_parsed_question_from_dict(question) for question in data['questions']]
    unsupported = [_parsed_question_from_dict(question) for question in data['unsupported']]
    items = _question_forms_from_parsed(questions, question_format.code)

    return render(request, 'teaching/subject/question/import_review/page.html', {
        'subject': subject,
        'topic': topic,
        'import_id': import_id,
        'question_count': len(items),
        'items': items,
        'unsupported': unsupported,
        'format_code': question_format.code,
        'media': ImportedQuestionForm(format_code=question_format.code).media,
        'variant_codes_json': _variant_codes_json(question_format.code),
    })


# -------------- cancel (HTMX, confirm-gated) --------------
@partner_teacher_required
@require_POST
def question_import_cancel_view(request, pk, import_id):
    subject = owned_subject(request, pk)
    data = request.session.pop(_session_key(import_id), None)

    if data:
        for path in data.get('image_paths', []):
            default_storage.delete(path)

    response = HttpResponse(status=204)
    response['HX-Redirect'] = reverse('teaching:question-import', args=[subject.pk])
    return response


# -------------- confirm + save --------------
@partner_teacher_required
@require_POST
def question_import_confirm_view(request, pk, import_id):
    subject = owned_subject(request, pk)
    teacher = request.user.teacher
    data = request.session.get(_session_key(import_id))

    if not data:
        messages.error(request, _('This import session has expired or was already completed. Please upload the file again.'))
        return redirect('teaching:question-import', subject.pk)

    topic = _owned_topic(subject, data['topic_id'])
    question_format = get_question_format(data['format_id'])
    count = len(data['questions'])
    items = _question_forms_from_post(request.POST, count, question_format.code)

    all_valid = True
    for item in items:
        question_valid = item['question_form'].is_valid()
        option_valid = item['option_formset'].is_valid()
        pair_valid = item['pair_formset'].is_valid()

        if not (question_valid and option_valid and pair_valid):
            all_valid = False
            continue

        if not _validate_answer_data(question_format.code, item['question_form'], item['option_formset'], item['pair_formset']):
            all_valid = False

    if not all_valid:
        return render(request, 'teaching/subject/question/import_review/page.html', {
            'subject': subject,
            'topic': topic,
            'import_id': import_id,
            'question_count': count,
            'items': items,
            'unsupported': [],
            'format_code': question_format.code,
            'media': ImportedQuestionForm(format_code=question_format.code).media,
            'variant_codes_json': _variant_codes_json(question_format.code),
        })

    created = 0

    for item in items:
        question_form = item['question_form']
        if not question_form.cleaned_data.get('include'):
            continue

        options = None
        match_pairs = None

        if question_format.code == 'test':
            options = [
                {'answer': option_form.cleaned_data['text'], 'is_correct': option_form.cleaned_data['is_correct']}
                for option_form in item['option_formset'].forms
                if option_form.cleaned_data and not option_form.cleaned_data.get('DELETE')
            ]
        elif question_format.code == 'matching':
            match_pairs = [
                {'left': pair_form.cleaned_data['left'], 'right': pair_form.cleaned_data['right']}
                for pair_form in item['pair_formset'].forms
                if pair_form.cleaned_data and not pair_form.cleaned_data.get('DELETE')
            ]

        create_question(
            topic=topic,
            author=teacher,
            text=question_form.cleaned_data['text'],
            format=question_format,
            variant=question_form.cleaned_data['variant'],
            level=question_form.cleaned_data['level'],
            time_limit=question_form.cleaned_data['time_limit'],
            options=options,
            match_pairs=match_pairs,
        )

        created += 1

    del request.session[_session_key(import_id)]

    messages.success(request, _('{} questions imported successfully.').format(created))
    return redirect('teaching:question-list', subject.pk)
