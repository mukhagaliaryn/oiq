from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from requests import session

from core.models import GameTask, Activity, Question, GameTaskQuestion, Subject, Chapter, Topic, GameTaskSession
from core.utils.decorators import role_required


# Game task create
# ----------------------------------------------------------------------------------------------------------------------
# game_task_create
@role_required('teacher')
def game_task_create_view(request):
    user = request.user
    drafts = GameTask.objects.filter(owner=user, status='draft').order_by('-id')
    draft_count = drafts.count()

    if draft_count >= 3:
        last_draft = drafts.first()
        messages.warning(request, 'Сізде 3 аяқталмаған ойын тапсырмасы бар. Алдымен солардың бірін аяқтаңыз.')
        if last_draft:
            return redirect('teacher:game_task_edit', pk=last_draft.pk)


    game_task = GameTask.objects.create(
        name='',
        owner=user,
        subject=None,
        activity=None,
        status='draft'
    )
    return redirect('teacher:game_task_edit', pk=game_task.pk)


# get_game_task_current_step
def get_game_task_current_step(game_task: GameTask) -> str:
    if game_task.activity_id is None:
        return 'activity'
    if not game_task.questions.exists():
        return 'questions'
    if not game_task.name:
        return 'settings'
    return 'settings'


# game_task_edit
@role_required('teacher')
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
    return render(request, 'app/dashboard/teacher/game_tasks/edit/page.html', context)


# game_task_step_activity
@role_required('teacher')
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

        return redirect('teacher:game_task_step_questions', pk=game_task.pk)

    return render(
        request,
        'app/dashboard/teacher/game_tasks/edit/steps/activity.html',
        {
            'game_task': game_task,
            'activities': activities,
            'games': games,
            'simulators': simulators,
        }
    )


# game_task_step_questions
@role_required('teacher')
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

    error_message = None

    if request.method == 'POST':
        if not subject_id:
            error_message = 'Алдымен пәнді таңдаңыз.'
        else:
            if game_task.subject_id != int(subject_id):
                game_task.subject_id = subject_id
                game_task.save()

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

            if total_count <= 0:
                error_message = 'Сұрақ санын дұрыс енгізіңіз.'
            else:
                if not selected_levels:
                    level_codes = ['easy', 'medium', 'hard']
                else:
                    level_codes = selected_levels

                base_part = total_count // len(level_codes)
                remainder = total_count % len(level_codes)

                level_to_target_count = {}
                for idx, code in enumerate(level_codes):
                    extra = 1 if idx < remainder else 0
                    level_to_target_count[code] = base_part + extra

                GameTaskQuestion.objects.filter(game_task=game_task).delete()
                picked_questions = []
                total_picked = 0

                for level_code in level_codes:
                    need = level_to_target_count.get(level_code, 0)
                    if need <= 0:
                        continue

                    qs_level = qs.filter(level=level_code)
                    for q in qs_level.order_by('?')[:need]:
                        picked_questions.append(q)
                        total_picked += 1

                if total_picked == 0:
                    error_message = 'Берілген фильтр бойынша сұрақ табылмады.'
                else:
                    if total_picked < total_count:
                        error_message = (
                            f'Берілген фильтр бойынша тек {total_picked} сұрақ табылды. '
                            f'Қалғаны базада жоқ.'
                        )

                    level_priority = {'easy': 0, 'medium': 1, 'hard': 2}
                    picked_questions.sort(
                        key=lambda q: (level_priority.get(q.level, 99), q.id)
                    )
                    order = 1
                    for q in picked_questions:
                        GameTaskQuestion.objects.create(game_task=game_task, question=q, order=order)
                        order += 1

    selected_questions = (
        GameTaskQuestion.objects.filter(game_task=game_task)
        .select_related('question', 'question__topic', 'question__topic__chapter', )
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
    }
    return render(
        request,
        'app/dashboard/teacher/game_tasks/edit/steps/questions.html',
        context
    )


# game_task_step_settings
@role_required('teacher')
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
        'selected_questions_count': selected_questions_count,
        'can_publish': can_publish,
    }
    return render(request, 'app/dashboard/teacher/game_tasks/edit/steps/settings.html', context)


# game_task_publish_view
@role_required('teacher')
def game_task_publish_view(request, pk):
    game_task = get_object_or_404(GameTask, pk=pk, owner=request.user)

    if request.method == 'POST':
        if not game_task.name:
            messages.error(request, 'Алдымен ойынға атау беріңіз.')
            return redirect('teacher:game_task_edit', pk=game_task.pk)

        if not game_task.questions.exists():
            messages.error(request, 'Кем дегенде бір сұрақ генерациялау керек.')
            return redirect('teacher:game_task_edit', pk=game_task.pk)

        game_task.status = 'published'
        game_task.save()
        messages.success(request, 'Ойын тапсырмасы сәтті сақталды!')

        return redirect('teacher:game_task_detail', pk=game_task.pk)
    return redirect('teacher:game_task_step_settings', pk=game_task.pk)


# Game task detail page
# ----------------------------------------------------------------------------------------------------------------------
@role_required('teacher')
def game_task_detail_view(request, pk):
    game_task = get_object_or_404(GameTask, id=pk)
    sessions = GameTaskSession.objects.filter(game_task=game_task)

    context = {
        'game_task': game_task,
        'sessions': sessions,
    }
    return render(request, 'app/dashboard/teacher/game_tasks/game_task/page.html', context)


# Game task questions page
# ----------------------------------------------------------------------------------------------------------------------
@role_required('teacher')
def game_task_questions_view(request, pk):
    game_task = get_object_or_404(GameTask, id=pk)
    questions = GameTaskQuestion.objects.filter(game_task=game_task)

    context = {
        'game_task': game_task,
        'questions': questions,
    }
    return render(request, 'app/dashboard/teacher/game_tasks/game_task/questions/page.html', context)