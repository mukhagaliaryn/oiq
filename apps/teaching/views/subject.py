from django.contrib import messages
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from apps.catalog.selectors import (
    count_subject_topics, get_chapter, get_chapter_topics, get_chapters,
    get_subject_grades, get_subject_tree, get_topic, get_topic_question_formats,
    count_topic_questions_by_level,
)
from apps.catalog.services import (
    create_chapter, create_topic, delete_chapter, delete_topic,
    remove_subject_cover, update_chapter, update_subject, update_topic,
)
from apps.teaching.forms.subject import ChapterForm, SubjectForm, TopicForm
from apps.teaching.views.common import owned_subject
from apps.accounts.decorators import partner_teacher_required


def _render_with_toast(request, template, context, msg):
    messages.success(request, msg)
    html = render_to_string(template, context, request=request)
    toast = render_to_string('components/product/messages.html', {}, request=request)
    return HttpResponse(html + f'<div hx-swap-oob="beforeend:body">{toast}</div>', content_type='text/html; charset=utf-8')


def _owned_chapter(request, pk):
    teacher = request.user.teacher
    chapter = get_chapter(pk)

    if chapter.subject_id != teacher.subject_id:
        raise Http404

    return chapter


def _owned_topic(request, pk):
    teacher = request.user.teacher
    topic = get_topic(pk)

    if topic.chapter.subject_id != teacher.subject_id:
        raise Http404

    return topic


def _selected_grade(request, subject):
    grades = get_subject_grades(subject)
    return grades.filter(code=request.GET.get('grade')).first() or grades.first()


def _attach_topic_stats(topic):
    topic.level_breakdown = count_topic_questions_by_level(topic)
    topic.questions_count = sum(count for _label, count in topic.level_breakdown)
    topic.formats = get_topic_question_formats(topic)


def _chapters_section_context(request, subject, selected_grade, editing_chapter_id=None, chapter_edit_form=None):
    chapters = list(get_subject_tree(subject, grade=selected_grade))

    for chapter in chapters:
        if chapter_edit_form is not None and chapter.pk == editing_chapter_id:
            chapter.edit_form = chapter_edit_form
        else:
            chapter.edit_form = ChapterForm(
                instance=chapter, subject=subject, grade=selected_grade, prefix=f'chapter-{chapter.pk}',
            )

        chapter.topic_create_form = TopicForm(chapter=chapter, prefix=f'topic-create-{chapter.pk}')

        for topic in chapter.topics.all():
            topic.edit_form = TopicForm(instance=topic, chapter=chapter, prefix=f'topic-{topic.pk}')
            _attach_topic_stats(topic)

    return {
        'subject': subject,
        'selected_grade': selected_grade,
        'chapters': chapters,
        'chapter_form': ChapterForm(subject=subject, grade=selected_grade, prefix='chapter-create'),
        'editing_chapter_id': editing_chapter_id,
    }


def _topics_section_context(chapter, editing_topic_id=None, topic_edit_form=None):
    topics = list(get_chapter_topics(chapter))

    for topic in topics:
        if topic_edit_form is not None and topic.pk == editing_topic_id:
            topic.edit_form = topic_edit_form
        else:
            topic.edit_form = TopicForm(instance=topic, chapter=chapter, prefix=f'topic-{topic.pk}')
        _attach_topic_stats(topic)

    return {
        'chapter': chapter,
        'topics': topics,
        'topic_create_form': TopicForm(chapter=chapter, prefix=f'topic-create-{chapter.pk}'),
        'editing_topic_id': editing_topic_id,
    }


def _subject_info_context(subject):
    return {
        'subject': subject,
        'chapters_count': get_chapters(subject).count(),
        'topics_count': count_subject_topics(subject),
        'grades_count': get_subject_grades(subject).count(),
    }


# Subject
# ----------------------------------------------------------------------------------------------------------------------
# -------------- subject edit form (HTMX) --------------
@partner_teacher_required
def subject_update_view(request, pk):
    subject = owned_subject(request, pk)

    if request.method == 'POST':
        form = SubjectForm(request.POST, request.FILES, instance=subject)
        if form.is_valid():
            subject = update_subject(
                subject,
                name=form.cleaned_data['name'],
                description=form.cleaned_data['description'],
                cover=form.cleaned_data['cover'],
            )
            messages.success(request, _('Subject updated successfully.'))
            info_html = render_to_string(
                'teaching/subject/_subject_info.html', _subject_info_context(subject), request=request
            )
            toast_html = render_to_string('components/product/messages.html', {}, request=request)
            body = info_html + f'<div hx-swap-oob="beforeend:body">{toast_html}</div>'
            response = HttpResponse(body, content_type='text/html; charset=utf-8')
            response['HX-Retarget'] = '#subject-info'
            response['HX-Reswap'] = 'outerHTML'
            response['HX-Trigger'] = 'subject-updated'
            return response
    else:
        form = SubjectForm(instance=subject)

    return render(request, 'teaching/subject/_subject_edit_form.html', {
        'subject': subject,
        'form': form,
    })


# -------------- subject remove cover (HTMX) --------------
@partner_teacher_required
def subject_remove_cover_view(request, pk):
    subject = owned_subject(request, pk)
    subject = remove_subject_cover(subject)

    response = render(request, 'teaching/subject/_subject_info.html', _subject_info_context(subject))
    response['HX-Retarget'] = '#subject-info'
    response['HX-Reswap'] = 'outerHTML'
    response['HX-Trigger'] = 'subject-updated'
    return response


# -------------- subject detail --------------
@partner_teacher_required
def subject_detail_view(request, pk):
    subject = owned_subject(request, pk)
    grades = get_subject_grades(subject)
    selected_grade = _selected_grade(request, subject)

    context = _chapters_section_context(request, subject, selected_grade)
    context['grades'] = grades
    context.update(_subject_info_context(subject))

    return render(request, 'teaching/subject/page.html', context)


# Chapter
# ----------------------------------------------------------------------------------------------------------------------
# -------------- chapter create --------------
@partner_teacher_required
def chapter_create_view(request, pk):
    subject = owned_subject(request, pk)
    selected_grade = _selected_grade(request, subject)
    form = ChapterForm(request.POST, subject=subject, grade=selected_grade, prefix='chapter-create')

    if form.is_valid():
        create_chapter(
            subject=subject, grade=selected_grade,
            title=form.cleaned_data['title'], description=form.cleaned_data['description'],
            order=form.cleaned_data['order'],
        )
        return _render_with_toast(
            request, 'teaching/subject/_chapters_section.html',
            _chapters_section_context(request, subject, selected_grade),
            _('Chapter created successfully.'),
        )

    context = _chapters_section_context(request, subject, selected_grade)
    context['chapter_form'] = form
    context['show_chapter_form'] = True
    return render(request, 'teaching/subject/_chapters_section.html', context)


# -------------- chapter update --------------
@partner_teacher_required
def chapter_update_view(request, pk):
    chapter = _owned_chapter(request, pk)
    subject = chapter.subject
    selected_grade = _selected_grade(request, subject)
    form = ChapterForm(
        request.POST, instance=chapter, subject=subject, grade=selected_grade, prefix=f'chapter-{chapter.pk}',
    )

    if form.is_valid():
        update_chapter(
            chapter,
            title=form.cleaned_data['title'], description=form.cleaned_data['description'],
            order=form.cleaned_data['order'],
        )
        return _render_with_toast(
            request, 'teaching/subject/_chapters_section.html',
            _chapters_section_context(request, subject, selected_grade),
            _('Chapter updated successfully.'),
        )

    context = _chapters_section_context(
        request, subject, selected_grade,
        editing_chapter_id=chapter.pk, chapter_edit_form=form,
    )
    return render(request, 'teaching/subject/_chapters_section.html', context)


# -------------- chapter delete --------------
@partner_teacher_required
def chapter_delete_view(request, pk):
    chapter = _owned_chapter(request, pk)
    subject = chapter.subject
    selected_grade = _selected_grade(request, subject)

    delete_chapter(chapter)

    return _render_with_toast(
        request, 'teaching/subject/_chapters_section.html',
        _chapters_section_context(request, subject, selected_grade),
        _('Chapter deleted.'),
    )


# Topic
# ----------------------------------------------------------------------------------------------------------------------
# -------------- topic create --------------
@partner_teacher_required
def topic_create_view(request, pk):
    chapter = _owned_chapter(request, pk)
    form = TopicForm(request.POST, chapter=chapter, prefix=f'topic-create-{chapter.pk}')

    if form.is_valid():
        create_topic(
            chapter=chapter, title=form.cleaned_data['title'],
            description=form.cleaned_data['description'], order=form.cleaned_data['order'],
        )
        return _render_with_toast(
            request, 'teaching/subject/_topics_section.html',
            _topics_section_context(chapter),
            _('Topic created successfully.'),
        )

    context = _topics_section_context(chapter)
    context['topic_create_form'] = form
    context['show_topic_form'] = True
    return render(request, 'teaching/subject/_topics_section.html', context)


# -------------- topic update --------------
@partner_teacher_required
def topic_update_view(request, pk):
    topic = _owned_topic(request, pk)
    chapter = topic.chapter
    form = TopicForm(request.POST, instance=topic, chapter=chapter, prefix=f'topic-{topic.pk}')

    if form.is_valid():
        update_topic(
            topic, title=form.cleaned_data['title'],
            description=form.cleaned_data['description'], order=form.cleaned_data['order'],
        )
        return _render_with_toast(
            request, 'teaching/subject/_topics_section.html',
            _topics_section_context(chapter),
            _('Topic updated successfully.'),
        )

    context = _topics_section_context(chapter, editing_topic_id=topic.pk, topic_edit_form=form)
    return render(request, 'teaching/subject/_topics_section.html', context)


# -------------- topic delete --------------
@partner_teacher_required
def topic_delete_view(request, pk):
    topic = _owned_topic(request, pk)
    chapter = topic.chapter

    delete_topic(topic)

    return _render_with_toast(
        request, 'teaching/subject/_topics_section.html',
        _topics_section_context(chapter),
        _('Topic deleted.'),
    )
