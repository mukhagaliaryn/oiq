from django.db import transaction
from core.models import GameTask, Activity, Question, Subject


def build_game_task_context(wizard, errors=None):
    # жаңа Activity моделі:
    games = Activity.objects.filter(activity_type="game").order_by("order")
    simulators = Activity.objects.filter(activity_type="simulator").order_by("order")

    subjects = Subject.objects.all()

    form_values = {
        "activity_id": wizard.get("activity_id", ""),
        "subject_id": wizard.get("subject_id", ""),
        "chapter_id": wizard.get("chapter_id", ""),
        "topic_id": wizard.get("topic_id", ""),
        "question_limit": wizard.get("question_limit", ""),
        "name": wizard.get("name", ""),
        "timer": wizard.get("timer", ""),
    }

    return {
        "games": games,
        "simulators": simulators,
        "subjects": subjects,
        "form_values": form_values,
        "errors": errors or {},
    }


def finish_game_task_wizard(teacher, wizard):
    errors = {}

    activity_id = wizard.get("activity_id")
    subject_id = wizard.get("subject_id")
    question_limit_raw = wizard.get("question_limit")
    name = (wizard.get("name") or "").strip()
    timer_raw = wizard.get("timer")  # қайда қолданатыныңды өзің шешесің
    chapter_id = wizard.get("chapter_id") or None
    topic_id = wizard.get("topic_id") or None

    # Activity
    activity = None
    try:
        activity = Activity.objects.get(pk=activity_id)
    except (Activity.DoesNotExist, TypeError, ValueError):
        errors["activity_id"] = "Интерактивті дұрыс таңдаңыз."

    # Subject
    subject = teacher.subjects.filter(pk=subject_id).first()
    if not subject:
        errors["subject_id"] = "Пәнді дұрыс таңдаңыз."

    # Question limit
    question_limit = None
    try:
        question_limit = int(question_limit_raw or 0)
        if question_limit <= 0:
            raise ValueError
    except ValueError:
        errors["question_limit"] = "Сұрақ санын дұрыс енгізіңіз."

    # Name
    if not name:
        errors["name"] = "Ойын тапсырмасының атауын енгізіңіз."

    if errors:
        return errors

    # Сұрақтарды таңдау (жаңа Activity.question_formats-ты ескере отырып)
    question_ids = select_questions(
        activity=activity,
        subject=subject,
        question_limit=question_limit,
        chapter_id=chapter_id,
        topic_id=topic_id,
    )

    if not question_ids:
        errors["question_limit"] = "Берілген параметрлерге сәйкес сұрақ табылмады."
        return errors

    # GameTask құру
    with transaction.atomic():
        game_task = GameTask.objects.create(
            owner=teacher,
            activity=activity,
            subject=subject,
            name=name,
            question_limit=question_limit,
            # егер GameTask-та default_duration немесе timer деген өріс қоссаң:
            # default_duration=timer,
        )
        game_task.questions.set(question_ids)

    return game_task


def select_questions(activity, subject, question_limit, chapter_id=None, topic_id=None):
    base_qs = Question.objects.filter(
        topic__chapter__subject=subject,
        format__in=activity.question_formats.all(),  # жаңа ManyToMany атауы
    )

    if topic_id:
        base_qs = base_qs.filter(topic_id=topic_id)
    elif chapter_id:
        base_qs = base_qs.filter(topic__chapter_id=chapter_id)

    # difficulty балансы (easy/medium/hard) – сенің ескі логикаңды адаптациялап
    levels = ["easy", "medium", "hard"]
    per = question_limit // 3
    rem = question_limit % 3

    selected_ids = []
    for i, lvl in enumerate(levels):
        limit = per + (1 if i < rem else 0)
        if limit <= 0:
            continue
        qs = base_qs.filter(level=lvl).order_by("?")[:limit]
        selected_ids += list(qs.values_list("id", flat=True))

    if len(selected_ids) < question_limit:
        extra = (
            base_qs.exclude(id__in=selected_ids)
            .order_by("?")[: question_limit - len(selected_ids)]
        )
        selected_ids += list(extra.values_list("id", flat=True))

    return selected_ids[:question_limit]