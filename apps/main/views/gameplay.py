from django.db import transaction, IntegrityError
from django.db.models.aggregates import Avg
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from apps.main.services.gameplay import cleanup_session_token_if_matches, get_participant_or_redirect, \
    hx_redirect, guard_session_state, load_questions, finish_participant
from apps.main.services.gameplay_play import calculate_question_score, resolve_activity_template, \
    get_or_create_options_in_fixed_order
from apps.main.services.gameplay_join import get_joinable_session_by_pin, get_unique_nickname_for_session, \
    join_validation
from core.models import Participant, QuestionAttempt, TestAnswer, Option


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
            'game_task': game_task,
        })

    current_gtq = questions[attempts_count]
    current_question = current_gtq.question

    if participant.current_question_id != current_question.id:
        participant.current_question_id = current_question.id
        participant.current_started_at = timezone.now()
        participant.save(update_fields=['current_question_id', 'current_started_at'])

    options_qs, options_order = get_or_create_options_in_fixed_order(request, participant, current_question)
    options = list(options_qs)

    question_limit = getattr(current_question, 'question_limit', 0) or 0
    started_at = participant.current_started_at or timezone.now()
    elapsed = int((timezone.now() - started_at).total_seconds())
    remaining_seconds = max(0, question_limit - max(0, elapsed))

    context = {
        'participant': participant,
        'session': session,
        'game_task': game_task,
        'question': current_question,
        'gtq': current_gtq,
        'options': options,
        'index': attempts_count + 1,
        'total_questions': total_questions,
        'question_limit': question_limit,
        'remaining_seconds': remaining_seconds,
    }
    tpl = resolve_activity_template(game_task.activity, '_question.html')
    return render(request, tpl, context)


# gameplay_answer_action
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
            if attempts_count >= total_questions:
                finish_participant(participant)
                context = {
                    'participant': participant,
                    'session': session,
                    'game_task': game_task
                }
                tpl = resolve_activity_template(game_task.activity, '_finished.html')
                return render(request, tpl, context)

            current_gtq = questions[attempts_count]
            current_question = current_gtq.question

            now = timezone.now()
            if participant.current_started_at:
                time_spent = int((now - participant.current_started_at).total_seconds())
            else:
                time_spent = 0
            if time_spent < 0:
                time_spent = 0

            selected_ids = [int(pk) for pk in request.POST.getlist('options') if pk.isdigit()]
            if is_timeout:
                selected_ids = []

            allowed_ids = set(current_question.options.values_list('id', flat=True))
            selected_ids = [i for i in selected_ids if i in allowed_ids]
            selected_set = set(selected_ids)
            correct_ids = set(current_question.options.filter(is_correct=True).values_list('id', flat=True))

            if not correct_ids:
                is_correct = False
            else:
                q_type = current_question.variant.code if current_question.variant else 'single'
                if q_type == 'multiple':
                    is_correct = (selected_set == correct_ids)
                else:
                    one = next(iter(selected_set), None)
                    is_correct = (len(selected_set) == 1 and one in correct_ids)

            score_result = calculate_question_score(
                question=current_question,
                is_correct=is_correct,
                time_spent=time_spent,
            )
            score_delta = score_result.score
            attempt = QuestionAttempt.objects.create(
                participant=participant,
                question=current_question,
                is_correct=is_correct,
                score=score_delta,
                time_spent=time_spent,
            )

            test_answer = TestAnswer.objects.create(attempt=attempt)
            if selected_ids:
                test_answer.selected_options.set(Option.objects.filter(id__in=selected_ids))

            participant.current_question_id = None
            participant.current_started_at = None
            if is_correct:
                participant.correct_count += 1
                participant.score += score_delta
            answered = bool(selected_ids) and not is_timeout

            participant.save(update_fields=['current_question_id', 'current_started_at', 'correct_count', 'score'])

    except IntegrityError:
        return hx_redirect(reverse('main:gameplay_question', kwargs={'token': token}))

    options_qs, options_order = get_or_create_options_in_fixed_order(request, participant, current_question)
    options = list(options_qs)

    context = {
        'participant': participant,
        'session': session,
        'game_task': game_task,
        'question': current_question,
        'options': options,
        'index': attempts_count + 1,
        'total_questions': total_questions,
        'selected_ids': selected_ids,
        'correct_ids': correct_ids,
        'last_answer_correct': is_correct if answered else None,
        'answered': answered,
        'score_delta': score_delta if is_correct else 0,
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


# gameplay_result_view
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
