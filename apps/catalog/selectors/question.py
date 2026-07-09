from django.db.models import Count
from django.shortcuts import get_object_or_404
from apps.catalog.models import FormatVariant, Question, QuestionFormat


def get_questions_for_topic(topic_id, level=None):
    questions = Question.objects.filter(topic_id=topic_id, is_active=True)
    if level:
        questions = questions.filter(level=level)
    return questions


def get_questions(*, subject=None, author=None, grade_id=None, chapter_id=None, topic_id=None,
                   format_id=None, variant_id=None, search=None):
    questions = Question.objects.filter(is_active=True)

    if subject is not None:
        questions = questions.filter(topic__chapter__subject=subject)
    if author is not None:
        questions = questions.filter(author=author)
    if grade_id:
        questions = questions.filter(topic__chapter__grade_id=grade_id)
    if chapter_id:
        questions = questions.filter(topic__chapter_id=chapter_id)
    if topic_id:
        questions = questions.filter(topic_id=topic_id)
    if format_id:
        questions = questions.filter(format_id=format_id)
    if variant_id:
        questions = questions.filter(variant_id=variant_id)
    if search:
        questions = questions.filter(text__icontains=search)

    return questions.select_related('topic', 'topic__chapter', 'format', 'variant').order_by('-created_at')


def get_question(pk):
    return get_object_or_404(Question.objects.filter(is_active=True), pk=pk)


def get_question_formats():
    return QuestionFormat.objects.order_by('order')


def get_question_format_by_code(code):
    return QuestionFormat.objects.get(code=code)


def get_format_variants(format_id):
    if not format_id:
        return FormatVariant.objects.none()
    return FormatVariant.objects.filter(format_id=format_id).order_by('order')


def get_format_variants_by_format_code(code):
    return FormatVariant.objects.filter(format__code=code).order_by('order')


def get_all_format_variants():
    return FormatVariant.objects.all()


def count_topic_questions_by_level(topic):
    counts_by_level = dict(
        Question.objects.filter(topic=topic, is_active=True)
        .values_list('level')
        .annotate(count=Count('id'))
    )
    return [(label, counts_by_level.get(value, 0)) for value, label in Question.Level.choices]


def get_topic_question_formats(topic):
    return list(
        Question.objects.filter(topic=topic, is_active=True)
        .values_list('format__name', flat=True).distinct()
    )
