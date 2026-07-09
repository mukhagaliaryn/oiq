from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from apps.catalog.models import Chapter, Subject, Topic


def get_subject(pk):
    return get_object_or_404(Subject.objects.filter(is_active=True), pk=pk)


def get_active_subjects():
    return Subject.objects.filter(is_active=True).order_by('order')


def get_subject_tree(subject, grade=None):
    chapters = subject.chapters.filter(is_active=True)
    if grade is not None:
        chapters = chapters.filter(Q(grade__isnull=True) | Q(grade=grade))

    return chapters.order_by('order').prefetch_related(
        Prefetch('topics', queryset=Topic.objects.filter(is_active=True).order_by('order')),
    )


def get_subject_grades(subject):
    return subject.grades.filter(is_active=True).order_by('order')


def get_chapters(subject, grade_id=None):
    chapters = Chapter.objects.filter(subject=subject, is_active=True)
    if grade_id:
        chapters = chapters.filter(Q(grade_id=grade_id) | Q(grade__isnull=True))
    return chapters.order_by('order')


def get_chapter(pk):
    return get_object_or_404(Chapter.objects.filter(is_active=True), pk=pk)


def get_topics(subject, chapter_id=None, grade_id=None):
    topics = Topic.objects.filter(chapter__subject=subject, is_active=True).select_related('chapter')
    if chapter_id:
        topics = topics.filter(chapter_id=chapter_id)
    elif grade_id:
        topics = topics.filter(Q(chapter__grade_id=grade_id) | Q(chapter__grade__isnull=True))
    return topics.order_by('chapter__order', 'order')


def get_topic(pk):
    return get_object_or_404(Topic.objects.filter(is_active=True), pk=pk)


def get_chapter_topics(chapter):
    return chapter.topics.filter(is_active=True).order_by('order')


def count_subject_topics(subject):
    return Topic.objects.filter(chapter__subject=subject, is_active=True).count()
