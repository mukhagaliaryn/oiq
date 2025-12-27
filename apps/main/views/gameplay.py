from django.db import transaction, IntegrityError
from django.db.models.aggregates import Avg
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from core.models import Participant, QuestionAttempt
from apps.main.services.gameplay import cleanup_session_token_if_matches, get_participant_or_redirect, \
    hx_redirect, guard_session_state, load_questions, finish_participant
from apps.main.services.gameplay_play import resolve_activity_template
from apps.main.services.gameplay_join import get_joinable_session_by_pin, get_unique_nickname_for_session, \
    join_validation
from apps.main.handlers.gameplay.registry import get_handler_for_question


# ----------------------------------------------------------------------------------------------------------------------
# gameplay_join page
# ----------------------------------------------------------------------------------------------------------------------
@require_http_methods(['GET', 'POST'])
def gameplay_join_view(request):
    if request.method == 'GET':
        token = request.session.get('current_game_participant_token')
        participant = None
        if token:
            participant = (
                Participant.objects
                .select_related('session', 'session__game_task')
                .filter(token=token)
                .first()
            )
        if participant:
            session = participant.session
            if session.is_pending():
                return redirect('main:gameplay_waiting', token=participant.token)
            if session.is_active():
                return redirect('main:gameplay_play', token=participant.token)

            cleanup_session_token_if_matches(request, participant)

        pin_prefill = (request.GET.get('pin') or '').strip()
        context = {
            'pin_prefill': pin_prefill,
            'error': None,
            'field_errors': {},
        }
        return render(request, 'app/main/gameplay/join/page.html', context)

    # -------------------- POST --------------------
    pin_code, nickname, errors = join_validation(request.POST.get('pin'), request.POST.get('nickname'))
    if errors:
        context = {
            'pin_prefill': pin_code,
            'error': 'Деректерді дұрыс енгізіңіз.',
            'field_errors': errors,
        }
        return render(request, 'app/main/gameplay/join/page.html', context)

    session = get_joinable_session_by_pin(pin_code)
    if not session:
        context = {
            'pin_prefill': pin_code,
            'error': 'Сессия табылмады немесе басталып/аяқталып кетті.',
            'field_errors': {},
        }
        return render(request, 'app/main/gameplay/join/page.html', context)

    token = request.session.get('current_game_participant_token')
    participant = None
    if token:
        participant = Participant.objects.filter(token=token, session=session).first()
    if not participant:
        final_nickname = get_unique_nickname_for_session(session, nickname)
        participant = Participant.objects.create(session=session, nickname=final_nickname)

    request.session['current_game_participant_token'] = str(participant.token)
    return redirect('main:gameplay_waiting', token=participant.token)


# ----------------------------------------------------------------------------------------------------------------------
# gameplay_waiting page
# ----------------------------------------------------------------------------------------------------------------------
@require_GET
def gameplay_waiting_view(request, token):
    participant, err = get_participant_or_redirect(request, token, for_htmx=False)
    if err:
        return err

    session = participant.session
    game_task = session.game_task
    if session.is_time_over() or session.is_finished():
        cleanup_session_token_if_matches(request, participant)
        return redirect('main:gameplay_join')

    if session.is_active():
        if not participant.started_at:
            participant.started_at = timezone.now()
            participant.save(update_fields=['started_at'])
        return redirect('main:gameplay_play', token=token)

    context = {
        'participant': participant,
        'session': session,
        'game_task': game_task,
    }
    return render(request, 'app/main/gameplay/waiting/page.html', context)


# gameplay_waiting_poll
# ----------------------------------------------------------------------------------------------------------------------
@require_GET
def gameplay_waiting_poll_fragment(request, token):
    participant, err = get_participant_or_redirect(request, token, for_htmx=True)
    if err:
        return err

    session = participant.session
    if session.is_time_over() or session.is_finished():
        cleanup_session_token_if_matches(request, participant)
        return hx_redirect(reverse('main:gameplay_join'))

    if session.is_active():
        return hx_redirect(reverse('main:gameplay_play', kwargs={'token': token}))

    return HttpResponse(status=204)


# ----------------------------------------------------------------------------------------------------------------------
# gameplay_play page
# ----------------------------------------------------------------------------------------------------------------------
@require_GET
def gameplay_play_view(request, token):
    participant, err = get_participant_or_redirect(request, token, for_htmx=False)
    if err:
        return err
    session, guard = guard_session_state(participant, token=token, for_htmx=False)
    if guard:
        return guard

    game_task = session.game_task
    total_questions = game_task.questions.count()
    if total_questions == 0:
        finish_participant(participant)
        return redirect('main:gameplay_result', token=token)

    attempts_count = participant.attempts.count()
    if attempts_count >= total_questions:
        finish_participant(participant)
        return redirect('main:gameplay_result', token=token)

    context = {
        'participant': participant,
        'session': session,
        'game_task': game_task,
        'index': attempts_count + 1,
        'total_questions': total_questions,
    }
    tpl = resolve_activity_template(game_task.activity, 'page.html')
    return render(request, tpl, context)


# gameplay_question_fragment
# ----------------------------------------------------------------------------------------------------------------------
@require_GET
def gameplay_question_fragment(request, token):
    participant, err = get_participant_or_redirect(request, token, for_htmx=True)
    if err:
        return err
    session, guard = guard_session_state(participant, token=token, for_htmx=True)
    if guard:
        return guard

    game_task = session.game_task
    questions = load_questions(game_task)
    total_questions = len(questions)
    attempts_count = participant.attempts.count()

    if total_questions == 0 or attempts_count >= total_questions:
        finish_participant(participant)
        tpl = resolve_activity_template(game_task.activity, '_finished.html')
        return render(request, tpl, {
            'participant': participant,
            'session': session,
            'game_task': game_task
        })

    current_gtq = questions[attempts_count]
    current_question = current_gtq.question
    if participant.current_question_id != current_question.id:
        participant.current_question_id = current_question.id
        participant.current_started_at = timezone.now()
        participant.save(update_fields=['current_question_id', 'current_started_at'])

    handler = get_handler_for_question(current_question)
    format_ctx = handler.get_question_context(
        request=request,
        participant=participant,
        question=current_question,
        gtq=current_gtq,
    )

    question_limit = getattr(current_question, 'question_limit', 0) or 0
    q_format = current_question.format.code if current_question.format else 'test'
    started_at = participant.current_started_at or timezone.now()
    elapsed = int((timezone.now() - started_at).total_seconds())
    remaining_seconds = max(0, question_limit - max(0, elapsed))

    context = {
        'participant': participant,
        'session': session,
        'game_task': game_task,
        'question': current_question,
        'gtq': current_gtq,
        'index': attempts_count + 1,
        'total_questions': total_questions,
        'question_limit': question_limit,
        'remaining_seconds': remaining_seconds,
        **format_ctx,
        'option_template': f"./partials/{q_format}/_options.html",
    }
    tpl = resolve_activity_template(game_task.activity, '_question.html')
    return render(request, tpl, context)


# gameplay_answer_action
# ----------------------------------------------------------------------------------------------------------------------
@require_POST
def gameplay_answer_action(request, token):
    participant, err = get_participant_or_redirect(request, token, for_htmx=True)
    if err:
        return err
    session, guard = guard_session_state(participant, token=token, for_htmx=True)
    if guard:
        return guard

    game_task = session.game_task
    is_timeout = request.POST.get('timeout') == '1'

    try:
        with transaction.atomic():
            participant = (
                Participant.objects
                .select_for_update()
                .select_related('session', 'session__game_task')
                .get(pk=participant.pk)
            )
            session = participant.session
            if session.is_time_over() or session.is_finished() or participant.is_finished:
                return hx_redirect(reverse('main:gameplay_result', kwargs={'token': token}))

            questions = load_questions(game_task)
            total_questions = len(questions)
            attempts_count = participant.attempts.count()

            if total_questions == 0 or attempts_count >= total_questions:
                finish_participant(participant)
                tpl = resolve_activity_template(game_task.activity, '_finished.html')
                return render(request, tpl, {
                    'participant': participant,
                    'session': session,
                    'game_task': game_task
                })

            current_gtq = questions[attempts_count]
            current_question = current_gtq.question
            now = timezone.now()
            time_spent = int((now - participant.current_started_at).total_seconds()) if participant.current_started_at else 0
            if time_spent < 0:
                time_spent = 0

            handler = get_handler_for_question(current_question)
            result = handler.parse_and_grade(
                request=request,
                participant=participant,
                question=current_question,
                gtq=current_gtq,
                is_timeout=is_timeout,
                time_spent=time_spent,
            )
            attempt = QuestionAttempt.objects.create(
                participant=participant,
                question=current_question,
                is_correct=(result.is_correct is True),
                score=result.score_delta,
                time_spent=time_spent,
            )
            handler.save_answer(
                participant=participant,
                question=current_question,
                gtq=current_gtq,
                attempt=attempt,
                payload=result.payload,
            )

            participant.current_question_id = None
            participant.current_started_at = None
            if result.is_correct:
                participant.correct_count += 1
                participant.score += result.score_delta

            participant.save(update_fields=['current_question_id', 'current_started_at', 'correct_count', 'score'])

    except IntegrityError:
        return hx_redirect(reverse('main:gameplay_question', kwargs={'token': token}))

    handler = get_handler_for_question(current_question)
    review_ctx = handler.get_review_context(
        request=request,
        participant=participant,
        question=current_question,
        gtq=current_gtq,
        payload=result.payload,
    )
    format_ctx = handler.get_question_context(
        request=request, participant=participant, question=current_question, gtq=current_gtq
    )
    q_format = current_question.format.code if current_question.format else 'test'

    context = {
        'participant': participant,
        'session': session,
        'game_task': game_task,
        'question': current_question,
        'gtq': current_gtq,
        'index': attempts_count + 1,
        'total_questions': total_questions,
        'answered': result.answered,
        'last_answer_correct': result.is_correct if result.answered else None,
        'score_delta': result.score_delta if result.is_correct is True else 0,
        **format_ctx,
        **review_ctx,
        'remaining_seconds': 0,
        'result_template': f"./partials/{q_format}/_results.html",
    }

    tpl = resolve_activity_template(game_task.activity, '_review.html')
    return render(request, tpl, context)


# gameplay_finish_action
# ----------------------------------------------------------------------------------------------------------------------
@require_POST
def gameplay_finish_action(request, token):
    participant, err = get_participant_or_redirect(request, token, for_htmx=False)
    if err:
        return err

    session = participant.session
    if session.is_pending():
        return redirect('main:gameplay_waiting', token=token)

    finish_participant(participant)
    return redirect('main:gameplay_result', token=token)


# ----------------------------------------------------------------------------------------------------------------------
# gameplay_result page
# ----------------------------------------------------------------------------------------------------------------------
@require_GET
def gameplay_result_view(request, token):
    participant, err = get_participant_or_redirect(request, token, for_htmx=False)
    if err:
        return err

    session = participant.session
    game_task = session.game_task

    if session.is_pending():
        return redirect('main:gameplay_waiting', token=token)

    participants_qs = session.participants.all().order_by('-score', '-correct_count', 'finished_at')
    participants = list(participants_qs)
    total = len(participants)

    position = None
    for idx, p in enumerate(participants, start=1):
        if p.pk == participant.pk:
            position = idx
            break

    finished_count = participants_qs.filter(is_finished=True).count()
    avg_score = participants_qs.aggregate(avg=Avg('score'))['avg']
    attempts = (
        QuestionAttempt.objects
        .filter(participant=participant)
        .select_related('question')
        .prefetch_related('test_answers__selected_options', 'question__options')
        .order_by('pk')
    )

    context = {
        'participant': participant,
        'session': session,
        'game_task': game_task,
        'position': position,
        'total_participants': total,
        'finished_count': finished_count,
        'avg_score': avg_score,
        'attempts': attempts,
    }
    return render(request, 'app/main/gameplay/result/page.html', context)
