from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.aggregates import Count
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from apps.dashboard.services.game_task_edit import get_game_task_current_step
from apps.dashboard.services.game_task_step_questions import generate_questions_for_game_task, \
    replace_game_task_questions
from core.models import GameTask, Activity, Question, GameTaskQuestion, Subject, Chapter, Topic, GameTaskSession


# game_task_create page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def game_task_create_action(request):
    user = request.user
    drafts = GameTask.objects.filter(owner=user, status='draft').order_by('-id')
    draft_count = drafts.count()

    if draft_count >= 3:
        last_draft = drafts.first()
        messages.warning(
            request,
            'Сізде 3 аяқталмаған ойын тапсырмасы бар. Алдымен солардың бірін аяқтаңыз.'
        )
        if last_draft:
            return redirect('dashboard:game_task_edit', pk=last_draft.pk)

    game_task = GameTask.objects.create(name='', owner=user, subject=None, activity=None, status='draft')
    return redirect('dashboard:game_task_edit', pk=game_task.pk)


# game_task_edit page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def game_task_edit_view(request, pk):
    game_task = get_object_or_404(GameTask, pk=pk, owner=request.user)
    current_step = get_game_task_current_step(game_task)
    step_activity_done = game_task.activity_id is not None
    step_questions_done = game_task.questions.exists()
    step_settings_done = bool(game_task.name)

    context = {
        'game_task': game_task,
        'current_step': current_step,
        'step_activity_done': step_activity_done,
        'step_questions_done': step_questions_done,
        'step_settings_done': step_settings_done,
    }
    return render(request, 'app/dashboard/game_tasks/edit/page.html', context)


# game_task_step_activity
@login_required
def game_task_step_activity(request, pk):
    game_task = get_object_or_404(GameTask, pk=pk, owner=request.user)
    activities = Activity.objects.all().order_by('order')
    games = activities.filter(activity_type='game')
    simulators = activities.filter(activity_type='simulator')

    if request.method == 'POST':
        activity_id = request.POST.get('activity_id')
        if activity_id:
            game_task.activity_id = activity_id
            game_task.save()

        return redirect('dashboard:game_task_step_questions', pk=game_task.pk)

    context = {
        'game_task': game_task,
        'activities': activities,
        'games': games,
        'simulators': simulators,
    }
    return render(request, 'app/dashboard/game_tasks/edit/steps/activity.html', context)


# game_task_step_questions
@login_required
def game_task_step_questions(request, pk):
    game_task = get_object_or_404(GameTask, pk=pk, owner=request.user)
    base_qs = Question.objects.all()
    if game_task.activity:
        formats = game_task.activity.question_formats.all()
        base_qs = base_qs.filter(format__in=formats)

    subjects = Subject.objects.all()
    subject_id = request.GET.get('subject_id') or request.POST.get('subject_id')
    chapter_id = request.GET.get('chapter_id') or request.POST.get('chapter_id')
    topic_id = request.GET.get('topic_id') or request.POST.get('topic_id')

    selected_levels = []
    error_message = None

    if not subject_id and game_task.subject_id:
        subject_id = str(game_task.subject_id)

    if subject_id:
        chapters = Chapter.objects.filter(subject_id=subject_id)
    else:
        chapters = Chapter.objects.none()
        chapter_id = None
        topic_id = None

    if chapter_id:
        topics = Topic.objects.filter(chapter_id=chapter_id)
    else:
        topics = Topic.objects.none()
        topic_id = None

    if request.method == 'POST':
        if not subject_id:
            error_message = 'Алдымен пәнді таңдаңыз.'
        else:
            if game_task.subject_id != int(subject_id):
                game_task.subject_id = subject_id
                game_task.save(update_fields=['subject'])

            qs = base_qs.filter(topic__chapter__subject_id=subject_id)
            if chapter_id:
                qs = qs.filter(topic__chapter_id=chapter_id)
            if topic_id:
                qs = qs.filter(topic_id=topic_id)

            selected_levels = request.POST.getlist('levels')
            try:
                total_count = int(request.POST.get('count') or 0)
            except ValueError:
                total_count = 0

            result = generate_questions_for_game_task(
                game_task=game_task,
                qs=qs,
                total_count=total_count,
                selected_levels=selected_levels or None,
            )
            if result.picked:
                replace_game_task_questions(game_task=game_task, questions=result.picked)

            error_message = result.warning

    selected_questions = (
        GameTaskQuestion.objects.filter(game_task=game_task)
        .select_related('question', 'question__topic', 'question__topic__chapter')
        .order_by('order')
    )

    context = {
        'game_task': game_task,
        'subjects': subjects,
        'chapters': chapters,
        'topics': topics,
        'selected_questions': selected_questions,
        'levels': Question.LEVEL,
        'current_subject_id': subject_id,
        'current_chapter_id': chapter_id,
        'current_topic_id': topic_id,
        'error_message': error_message,
        'selected_levels': selected_levels
    }
    return render(request, 'app/dashboard/game_tasks/edit/steps/questions.html', context)


# game_task_step_settings
@login_required
def game_task_step_settings(request, pk):
    game_task = get_object_or_404(GameTask, pk=pk, owner=request.user)
    selected_questions_count = game_task.questions.count()
    can_publish = False

    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        description = (request.POST.get('description') or '').strip()
        if name:
            game_task.name = name
            if hasattr(game_task, 'description'):
                game_task.description = description
            game_task.save()

            if selected_questions_count > 0:
                can_publish = True
        else:
            can_publish = False

    context = {
        'game_task': game_task,
        'can_publish': can_publish,
    }
    return render(request, 'app/dashboard/game_tasks/edit/steps/settings.html', context)


# game_task_publish_view
@login_required
def game_task_publish_view(request, pk):
    game_task = get_object_or_404(GameTask, pk=pk, owner=request.user)

    if request.method == 'POST':
        if not game_task.name:
            messages.error(request, 'Алдымен ойынға атау беріңіз.')
            return redirect('dashboard:game_task_edit', pk=game_task.pk)

        if not game_task.questions.exists():
            messages.error(request, 'Кем дегенде бір сұрақ генерациялау керек.')
            return redirect('dashboard:game_task_edit', pk=game_task.pk)

        game_task.status = 'published'
        game_task.save()
        messages.success(request, 'Ойын тапсырмасы сақталды!')

        return redirect('dashboard:game_task_detail', pk=game_task.pk)
    return redirect('dashboard:game_task_step_settings', pk=game_task.pk)


# game_task_delete action
@login_required
@require_POST
def game_task_delete_action(request, pk):
    game_task = get_object_or_404(GameTask, id=pk, owner=request.user)
    game_task.delete()
    messages.success(request, 'Ойын тапсырмасы жойылды!')
    return redirect('dashboard:game_tasks')


# game_task_detail page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def game_task_detail_view(request, pk):
    user = request.user
    game_task = (
        GameTask.objects
        .filter(owner=user, pk=pk)
        .annotate(total_participants=Count('sessions__participants', distinct=True))
        .select_related('activity', 'subject')
        .prefetch_related('questions', 'sessions')
        .get()
    )
    sessions = GameTaskSession.objects.filter(game_task=game_task)
    questions = GameTaskQuestion.objects.filter(game_task=game_task)

    context = {
        'game_task': game_task,
        'sessions': sessions,
        'questions': questions,
    }
    return render(request, 'app/dashboard/game_tasks/game_task/page.html', context)


# game_task_questions page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def game_task_questions_view(request, pk):
    user = request.user
    game_task = (
        GameTask.objects
        .filter(owner=user, pk=pk)
        .annotate(total_participants=Count('sessions__participants', distinct=True))
        .select_related('activity', 'subject')
        .prefetch_related('questions', 'sessions')
        .get()
    )
    sessions = GameTaskSession.objects.filter(game_task=game_task)
    questions = GameTaskQuestion.objects.filter(game_task=game_task)

    context = {
        'game_task': game_task,
        'sessions': sessions,
        'questions': questions
    }
    return render(request, 'app/dashboard/game_tasks/game_task/questions/page.html', context)
