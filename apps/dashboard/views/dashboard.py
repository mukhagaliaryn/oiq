from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from core.models import GameTask


# Dashboard page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def dashboard_view(request):
    user = request.user
    game_tasks = (
        GameTask.objects
        .filter(owner=user, status='published')
        .select_related('activity', 'subject')
        .prefetch_related('questions')
        .order_by('-pk')[:4]
    )

    drafts = GameTask.objects.filter(owner=user, status='draft').order_by('-id')
    draft_count = drafts.count()
    last_draft = drafts.first()

    context = {
        'game_tasks': game_tasks,
        'draft_count': draft_count,
        'last_draft': last_draft,
    }
    return render(request, 'app/dashboard/page.html', context)


# Game_tasks page
# ----------------------------------------------------------------------------------------------------------------------
@login_required
def game_tasks_view(request):
    user = request.user
    game_tasks = (
        GameTask.objects
        .filter(owner=user, status='published')
        .select_related('activity', 'subject')
        .prefetch_related('questions')
        .order_by('-pk')
    )
    context = {
        'game_tasks': game_tasks,
    }
    return render(request, 'app/dashboard/game_tasks/page.html', context)


@login_required
def game_task_drafts_view(request):
    user = request.user
    game_tasks = (
        GameTask.objects
        .filter(owner=user, status='draft')
        .select_related('activity', 'subject')
        .prefetch_related('questions')
        .order_by('-pk')
    )
    context = {
        'game_tasks': game_tasks,
    }
    return render(request, 'app/dashboard/game_tasks/drafts/page.html', context)


@login_required
def game_task_archives_view(request):
    user = request.user
    game_tasks = (
        GameTask.objects
        .filter(owner=user, status='archived')
        .select_related('activity', 'subject')
        .prefetch_related('questions')
        .order_by('-pk')
    )
    context = {
        'game_tasks': game_tasks,
    }
    return render(request, 'app/dashboard/game_tasks/archives/page.html', context)
