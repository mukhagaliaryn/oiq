import json
import uuid
from dataclasses import asdict

from django.contrib import messages
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

from apps.dashboard.teacher.forms.question_import import (
    ImportedOptionFormSet, ImportedQuestionForm, QuestionImportUploadForm,
)
from apps.dashboard.teacher.services.question_import import (
    ParsedOption, ParsedQuestion, QuestionImportError, run_question_import,
)
from apps.dashboard.teacher.views.common import owned_subject
from core.models import FormatVariant, Option, Question, QuestionFormat, Topic
from core.utils.decorators import partner_teacher_required

SESSION_KEY_PREFIX = 'question_import'


def _session_key(import_id):
    return f'{SESSION_KEY_PREFIX}:{import_id}'


def _parsed_question_from_dict(data):
    return ParsedQuestion(**{
        **data,
        'options': [ParsedOption(**option) for option in data['options']],
    })


def _variant_codes_json():
    return json.dumps({str(variant.id): variant.code for variant in FormatVariant.objects.filter(format__code='test')})


def _question_forms_from_parsed(questions):
    items = []
    for index, question in enumerate(questions):
        prefix = f'q{index}'
        variant = FormatVariant.objects.filter(format__code='test', code=question.variant_code).first()

        question_form = ImportedQuestionForm(prefix=prefix, initial={
            'include': True,
            'text': question.text_html,
            'variant': variant.pk if variant else None,
            'level': question.level,
            'time_limit': 30,
        })
        option_formset = ImportedOptionFormSet(prefix=f'{prefix}-options', initial=[
            {'text': option.text_html, 'is_correct': option.is_correct}
            for option in question.options
        ])

        items.append({'index': index, 'question_form': question_form, 'option_formset': option_formset, 'warning': question.warning})

    return items


def _question_forms_from_post(post_data, count):
    items = []
    for index in range(count):
        prefix = f'q{index}'
        question_form = ImportedQuestionForm(post_data, prefix=prefix)
        option_formset = ImportedOptionFormSet(post_data, prefix=f'{prefix}-options')

        items.append({'index': index, 'question_form': question_form, 'option_formset': option_formset, 'warning': ''})

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

            try:
                result = run_question_import(upload_form.cleaned_data['file'].read(), import_id)
            except QuestionImportError as error:
                messages.error(request, str(error))
                return render(request, 'app/dashboard/teacher/subject/question/import.html', {
                    'subject': subject, 'upload_form': upload_form,
                    'topic_fields_url': reverse('teacher:question-topic-fields'),
                })

            supported = [question for question in result.questions if question.is_supported]
            unsupported = [question for question in result.questions if not question.is_supported]

            if not supported:
                for path in result.image_paths:
                    default_storage.delete(path)

                messages.error(request, _('No importable questions were found in this file.'))
                return render(request, 'app/dashboard/teacher/subject/question/import.html', {
                    'subject': subject, 'upload_form': upload_form,
                    'topic_fields_url': reverse('teacher:question-topic-fields'),
                })

            request.session[_session_key(import_id)] = {
                'topic_id': upload_form.cleaned_data['topic'].pk,
                'questions': [asdict(question) for question in supported],
                'unsupported': [asdict(question) for question in unsupported],
                'image_paths': result.image_paths,
            }

            return redirect('teacher:question-import-review', subject.pk, import_id)
    else:
        upload_form = QuestionImportUploadForm(subject=subject)

    return render(request, 'app/dashboard/teacher/subject/question/import.html', {
        'subject': subject, 'upload_form': upload_form,
        'topic_fields_url': reverse('teacher:question-topic-fields'),
    })


# -------------- review (GET, reloadable — no AI call) --------------
@partner_teacher_required
def question_import_review_view(request, pk, import_id):
    subject = owned_subject(request, pk)
    data = request.session.get(_session_key(import_id))

    if not data:
        messages.error(request, _('This import session has expired or was already completed. Please upload the file again.'))
        return redirect('teacher:question-import', subject.pk)

    topic = get_object_or_404(Topic, pk=data['topic_id'], chapter__subject=subject, is_active=True)
    questions = [_parsed_question_from_dict(question) for question in data['questions']]
    unsupported = [_parsed_question_from_dict(question) for question in data['unsupported']]
    items = _question_forms_from_parsed(questions)

    return render(request, 'app/dashboard/teacher/subject/question/import_review.html', {
        'subject': subject,
        'topic': topic,
        'import_id': import_id,
        'question_count': len(items),
        'items': items,
        'unsupported': unsupported,
        'media': ImportedQuestionForm().media,
        'variant_codes_json': _variant_codes_json(),
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
    response['HX-Redirect'] = reverse('teacher:question-import', args=[subject.pk])
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
        return redirect('teacher:question-import', subject.pk)

    topic = get_object_or_404(Topic, pk=data['topic_id'], chapter__subject=subject, is_active=True)
    count = len(data['questions'])
    items = _question_forms_from_post(request.POST, count)

    all_valid = True
    for item in items:
        question_valid = item['question_form'].is_valid()
        options_valid = item['option_formset'].is_valid()

        if not (question_valid and options_valid):
            all_valid = False
            continue

        if item['question_form'].cleaned_data.get('include') and not _validate_option_rules(item['question_form'], item['option_formset']):
            all_valid = False

    if not all_valid:
        return render(request, 'app/dashboard/teacher/subject/question/import_review.html', {
            'subject': subject,
            'topic': topic,
            'import_id': import_id,
            'question_count': count,
            'items': items,
            'unsupported': [],
            'media': ImportedQuestionForm().media,
            'variant_codes_json': _variant_codes_json(),
        })

    test_format = QuestionFormat.objects.get(code='test')
    created = 0

    for item in items:
        question_form = item['question_form']
        if not question_form.cleaned_data.get('include'):
            continue

        question = Question.objects.create(
            topic=topic,
            author=teacher,
            text=question_form.cleaned_data['text'],
            format=test_format,
            variant=question_form.cleaned_data['variant'],
            level=question_form.cleaned_data['level'],
            time_limit=question_form.cleaned_data['time_limit'],
        )

        Option.objects.bulk_create([
            Option(
                question=question,
                answer=option_form.cleaned_data['text'],
                is_correct=option_form.cleaned_data['is_correct'],
            )
            for option_form in item['option_formset'].forms
            if option_form.cleaned_data and not option_form.cleaned_data.get('DELETE')
        ])

        created += 1

    del request.session[_session_key(import_id)]

    messages.success(request, _('{} questions imported successfully.').format(created))
    return redirect('teacher:question-list', subject.pk)
