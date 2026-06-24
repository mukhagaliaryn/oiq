from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404, render

from apps.dashboard.teacher.forms.subject import ChapterForm, TopicForm
from apps.dashboard.teacher.views.common import owned_subject
from core.models import Chapter, Question, Topic
from core.utils.decorators import partner_teacher_required


def _owned_chapter(request, pk):
    teacher = request.user.teacher
    return get_object_or_404(
        Chapter.objects.filter(subject_id=teacher.subject_id, is_active=True),
        pk=pk,
    )


def _owned_topic(request, pk):
    teacher = request.user.teacher
    return get_object_or_404(
        Topic.objects.filter(chapter__subject_id=teacher.subject_id, is_active=True),
        pk=pk,
    )


def _selected_grade(request, subject):
    grades = subject.grades.filter(is_active=True).order_by('order')
    return grades.filter(code=request.GET.get('grade')).first() or grades.first()


def _attach_topic_stats(topic):
    questions = topic.questions.filter(is_active=True)
    counts_by_level = dict(questions.values_list('level').annotate(count=Count('id')))

    topic.level_breakdown = [
        (label, counts_by_level.get(value, 0)) for value, label in Question.Level.choices
    ]
    topic.questions_count = sum(counts_by_level.values())
    topic.formats = list(questions.values_list('format__name', flat=True).distinct())


def _chapters_section_context(request, subject, selected_grade, editing_chapter_id=None, chapter_edit_form=None):
    chapters = list(
        subject.chapters
        .filter(is_active=True)
        .filter(Q(grade__isnull=True) | Q(grade=selected_grade))
        .order_by('order')
        .prefetch_related(
            Prefetch('topics', queryset=Topic.objects.filter(is_active=True).order_by('order')),
        )
    )

    for chapter in chapters:
        if chapter_edit_form is not None and chapter.pk == editing_chapter_id:
            chapter.edit_form = chapter_edit_form
        else:
            chapter.edit_form = ChapterForm(instance=chapter, subject=subject, prefix=f'chapter-{chapter.pk}')

        chapter.topic_create_form = TopicForm(chapter=chapter, prefix=f'topic-create-{chapter.pk}')

        for topic in chapter.topics.all():
            topic.edit_form = TopicForm(instance=topic, chapter=chapter, prefix=f'topic-{topic.pk}')
            _attach_topic_stats(topic)

    return {
        'subject': subject,
        'selected_grade': selected_grade,
        'chapters': chapters,
        'chapter_form': ChapterForm(subject=subject, prefix='chapter-create'),
        'editing_chapter_id': editing_chapter_id,
    }


def _topics_section_context(chapter, editing_topic_id=None, topic_edit_form=None):
    topics = list(chapter.topics.filter(is_active=True).order_by('order'))

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


# Subject
# ----------------------------------------------------------------------------------------------------------------------
# -------------- subject detail --------------
@partner_teacher_required
def subject_detail_view(request, pk):
    subject = owned_subject(request, pk)
    grades = subject.grades.filter(is_active=True).order_by('order')
    selected_grade = _selected_grade(request, subject)
    chapters_qs = subject.chapters.filter(is_active=True)

    context = _chapters_section_context(request, subject, selected_grade)
    context['grades'] = grades
    context['chapters_count'] = chapters_qs.count()
    context['topics_count'] = Topic.objects.filter(chapter__in=chapters_qs, is_active=True).count()
    context['grades_count'] = grades.count()

    return render(request, 'app/dashboard/teacher/subject/detail.html', context)


# Chapter
# ----------------------------------------------------------------------------------------------------------------------
# -------------- chapter create --------------
@partner_teacher_required
def chapter_create_view(request, pk):
    subject = owned_subject(request, pk)
    selected_grade = _selected_grade(request, subject)
    form = ChapterForm(request.POST, subject=subject, prefix='chapter-create')

    if form.is_valid():
        form.save()
        return render(
            request, 'app/dashboard/teacher/subject/_chapters_section.html',
            _chapters_section_context(request, subject, selected_grade),
        )

    context = _chapters_section_context(request, subject, selected_grade)
    context['chapter_form'] = form
    context['show_chapter_form'] = True
    return render(request, 'app/dashboard/teacher/subject/_chapters_section.html', context)


# -------------- chapter update --------------
@partner_teacher_required
def chapter_update_view(request, pk):
    chapter = _owned_chapter(request, pk)
    subject = chapter.subject
    selected_grade = _selected_grade(request, subject)
    form = ChapterForm(request.POST, instance=chapter, subject=subject, prefix=f'chapter-{chapter.pk}')

    if form.is_valid():
        form.save()
        return render(
            request, 'app/dashboard/teacher/subject/_chapters_section.html',
            _chapters_section_context(request, subject, selected_grade),
        )

    context = _chapters_section_context(
        request, subject, selected_grade,
        editing_chapter_id=chapter.pk, chapter_edit_form=form,
    )
    return render(request, 'app/dashboard/teacher/subject/_chapters_section.html', context)


# -------------- chapter delete --------------
@partner_teacher_required
def chapter_delete_view(request, pk):
    chapter = _owned_chapter(request, pk)
    subject = chapter.subject
    selected_grade = _selected_grade(request, subject)

    chapter.is_active = False
    chapter.save(update_fields=['is_active'])

    return render(
        request, 'app/dashboard/teacher/subject/_chapters_section.html',
        _chapters_section_context(request, subject, selected_grade),
    )


# Topic
# ----------------------------------------------------------------------------------------------------------------------
# -------------- topic create --------------
@partner_teacher_required
def topic_create_view(request, pk):
    chapter = _owned_chapter(request, pk)
    form = TopicForm(request.POST, chapter=chapter, prefix=f'topic-create-{chapter.pk}')

    if form.is_valid():
        form.save()
        return render(
            request, 'app/dashboard/teacher/subject/_topics_section.html',
            _topics_section_context(chapter),
        )

    context = _topics_section_context(chapter)
    context['topic_create_form'] = form
    context['show_topic_form'] = True
    return render(request, 'app/dashboard/teacher/subject/_topics_section.html', context)


# -------------- topic update --------------
@partner_teacher_required
def topic_update_view(request, pk):
    topic = _owned_topic(request, pk)
    chapter = topic.chapter
    form = TopicForm(request.POST, instance=topic, chapter=chapter, prefix=f'topic-{topic.pk}')

    if form.is_valid():
        form.save()
        return render(
            request, 'app/dashboard/teacher/subject/_topics_section.html',
            _topics_section_context(chapter),
        )

    context = _topics_section_context(chapter, editing_topic_id=topic.pk, topic_edit_form=form)
    return render(request, 'app/dashboard/teacher/subject/_topics_section.html', context)


# -------------- topic delete --------------
@partner_teacher_required
def topic_delete_view(request, pk):
    topic = _owned_topic(request, pk)
    chapter = topic.chapter

    topic.is_active = False
    topic.save(update_fields=['is_active'])

    return render(
        request, 'app/dashboard/teacher/subject/_topics_section.html',
        _topics_section_context(chapter),
    )
