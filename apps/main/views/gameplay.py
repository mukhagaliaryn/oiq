import re
from django.db.models.aggregates import Avg
from django.http import HttpResponse, HttpResponseNotAllowed
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from apps.main.services.gameplay_session_join import get_joinable_session_by_pin, get_unique_nickname_for_session
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
                .select_related('session')
                .filter(token=token)
                .first()
            )

        if participant:
            session = participant.session

            if session.is_time_over() or session.is_finished():
                request.session.pop('current_game_participant_token', None)
            else:
                if session.is_pending():
                    return redirect('main:gameplay_waiting', token=participant.token)
                if session.is_active():
                    return redirect('main:gameplay_play', token=participant.token)

                request.session.pop('current_game_participant_token', None)

        pin_prefill = (request.GET.get('pin') or '').strip()
        context = {
            'pin_prefill': pin_prefill,
            'error': None,
            'field_errors': {},
        }
        return render(request, 'app/main/gameplay/join/page.html', context)

    # -------------------- POST --------------------
    pin_code = (request.POST.get('pin') or '').strip()
    nickname = (request.POST.get('nickname') or '').strip()

    errors = {}
    if not pin_code:
        errors['pin'] = 'PIN кодты енгізіңіз.'

    if not nickname:
        errors['nickname'] = 'Есіміңізді (никнейм) енгізіңіз.'
    else:
        if len(nickname) > 20:
            errors['nickname'] = 'Есім ең көп дегенде 20 таңба болуы керек.'
        allowed_pattern = r"^[0-9A-Za-zА-Яа-яӘәІіҢңҒғҮүҰұҚқӨөЫыЁё ._'-]+$"
        if not re.match(allowed_pattern, nickname):
            errors['nickname'] = 'Есім тек әріп, цифра және қарапайым белгілерден тұруы керек.'

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
        participant = Participant.objects.filter(
            token=token,
            session=session,
        ).first()

    if not participant:
        final_nickname = get_unique_nickname_for_session(session, nickname)
        participant = Participant.objects.create(
            session=session,
            nickname=final_nickname,
            started_at=timezone.now(),
        )

    request.session['current_game_participant_token'] = str(participant.token)
    return redirect('main:gameplay_waiting', token=participant.token)


# gameplay_waiting page
# ----------------------------------------------------------------------------------------------------------------------
@require_GET
def gameplay_waiting_view(request, token):
    participant = get_object_or_404(
        Participant.objects.select_related('session', 'session__game_task'),
        token=token,
    )

    session_token = request.session.get('current_game_participant_token')
    if session_token != str(participant.token):
        return redirect('main:gameplay_join')

    session = participant.session
    game_task = session.game_task

    if session.is_time_over() or session.is_finished():
        if request.session.get('current_game_participant_token') == str(participant.token):
            request.session.pop('current_game_participant_token', None)
        return redirect('main:gameplay_join')

    if session.is_active():
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
    participant = get_object_or_404(
        Participant.objects.select_related('session'),
        token=token,
    )

    session_token = request.session.get('current_game_participant_token')
    if session_token != str(participant.token):
        resp = HttpResponse()
        resp['HX-Redirect'] = reverse('main:gameplay_join')
        return resp

    session = participant.session
    if session.is_time_over() or session.is_finished():
        resp = HttpResponse()
        resp['HX-Redirect'] = reverse('main:gameplay_join')
        return resp

    if session.is_active():
        resp = HttpResponse()
        resp['HX-Redirect'] = reverse('main:gameplay_play', kwargs={'token': token})
        return resp
    return HttpResponse(status=204)


# gameplay_play page
# ----------------------------------------------------------------------------------------------------------------------
def gameplay_play_view(request, token):
    participant = get_object_or_404(
        Participant.objects.select_related('session', 'session__game_task'),
        token=token,
    )
    session_token = request.session.get('current_game_participant_token')
    if session_token != str(participant.token):
        resp = HttpResponse()
        resp['HX-Redirect'] = reverse('main:gameplay_join')
        return resp

    session = participant.session
    game_task = session.game_task

    if session.is_pending():
        return redirect('main:gameplay_waiting', token=token)

    if session.is_finished():
        return redirect('main:gameplay_result', token=token)

    if participant.is_finished:
        return redirect('main:gameplay_result', token=token)

    questions_qs = (
        game_task.questions
        .select_related('question')
        .order_by('order', 'pk')
    )
    questions = list(questions_qs)
    total_questions = len(questions)
    attempts_count = participant.attempts.count()

    if attempts_count >= total_questions:
        if not participant.is_finished:
            participant.is_finished = True
            participant.finished_at = timezone.now()
            participant.save(update_fields=['is_finished', 'finished_at'])
        return redirect('main:gameplay_result', token=token)

    current_gtq = questions[attempts_count]
    current_question = current_gtq.question

    if participant.current_question_id != current_question.id:
        participant.current_question_id = current_question.id
        participant.current_started_at = timezone.now()
        participant.save(update_fields=['current_question_id', 'current_started_at'])

    options = getattr(current_question, 'options', None)
    if options is not None:
        options = options.all().order_by('?')

    context = {
        'participant': participant,
        'session': session,
        'game_task': game_task,
        'question': current_question,
        'gtq': current_gtq,
        'options': options,
        'index': attempts_count + 1,
        'total_questions': total_questions,
    }
    return render(request, 'app/main/gameplay/play/page.html', context)


# gt_session_answer_view
@require_POST
def gameplay_answer_action(request, token):
    participant = get_object_or_404(
        Participant.objects.select_related('session', 'session__game_task'),
        token=token,
    )
    session = participant.session
    game_task = session.game_task

    if session.is_pending():
        return redirect('main:gameplay_waiting', token=token)
    if session.is_finished():
        return redirect('main:gameplay_result', token=token)

    if participant.is_finished:
        return redirect('main:session_result', token=token)

    questions_qs = (
        game_task.questions
        .select_related('question')
        .order_by('order', 'pk')
    )
    questions = list(questions_qs)
    total_questions = len(questions)

    attempts_count = participant.attempts.count()

    if attempts_count >= total_questions:
        if not participant.is_finished:
            participant.is_finished = True
            participant.finished_at = timezone.now()
            participant.save(update_fields=['is_finished', 'finished_at'])
        return redirect('main:session_result', token=token)

    current_gtq = questions[attempts_count]
    current_question = current_gtq.question

    selected_ids = request.POST.getlist('options')
    selected_ids = [int(pk) for pk in selected_ids if pk.isdigit()]

    now = timezone.now()
    if participant.current_started_at:
        delta = now - participant.current_started_at
        time_spent = int(delta.total_seconds())
    else:
        time_spent = 0

    correct_options_qs = current_question.options.filter(is_correct=True)
    correct_ids = set(correct_options_qs.values_list('id', flat=True))
    selected_set = set(selected_ids)

    if not correct_ids:
        is_correct = False
    else:
        q_type = getattr(current_question, 'question_type', 'simple')

        if q_type == 'multiple':
            is_correct = (selected_set == correct_ids)
        else:
            is_correct = (
                len(selected_set) == 1 and
                list(selected_set)[0] in correct_ids
            )

    score_delta = 1 if is_correct else 0
    attempt = QuestionAttempt.objects.create(
        participant=participant,
        question=current_question,
        is_correct=is_correct,
        score_delta=score_delta,
        time_spent=time_spent,
    )

    test_answer = TestAnswer.objects.create(attempt=attempt)
    if selected_ids:
        selected_options_qs = Option.objects.filter(id__in=selected_ids)
        test_answer.selected_options.set(selected_options_qs)

    update_fields = ['current_question_id', 'current_started_at']
    participant.current_question_id = None
    participant.current_started_at = None

    if is_correct:
        participant.correct_count += 1
        participant.score += 1
        update_fields.extend(['correct_count', 'score'])

    participant.save(update_fields=update_fields)

    attempts_count += 1
    is_htmx = bool(request.headers.get('HX-Request'))

    if attempts_count >= total_questions:
        if not participant.is_finished:
            participant.is_finished = True
            participant.finished_at = timezone.now()
            participant.save(update_fields=['is_finished', 'finished_at'])

        if is_htmx:
            return render(request, 'app/main/gameplay/play/_finished.html', {
                'participant': participant,
                'session': session,
                'game_task': game_task,
            })

        return redirect('main:session_result', token=token)

    next_gtq = questions[attempts_count]
    next_question = next_gtq.question

    participant.current_question_id = next_question.id
    participant.current_started_at = timezone.now()
    participant.save(update_fields=['current_question_id', 'current_started_at'])

    options = getattr(next_question, 'options', None)
    if options is not None:
        options = options.all()

    context = {
        'participant': participant,
        'session': session,
        'game_task': game_task,
        'question': next_question,
        'gtq': next_gtq,
        'options': options,
        'index': attempts_count + 1,
        'total_questions': total_questions,
        'last_answer_correct': is_correct,
    }
    if is_htmx:
        return render(request, 'app/main/gameplay/play/_question.html', context)

    return redirect('main:session_play', token=token)


# gameplay_result_view
# ----------------------------------------------------------------------------------------------------------------------
def gameplay_result_view(request, token):
    participant = get_object_or_404(
        Participant.objects.select_related('session', 'session__game_task'),
        token=token,
    )
    session = participant.session
    game_task = session.game_task

    if session.is_pending():
        return redirect('main:gameplay_waiting', token=token)

    participants_qs = (
        session.participants
        .all()
        .order_by('-score', '-correct_count', 'finished_at')
    )

    participants = list(participants_qs)
    total = len(participants)

    position = None
    for idx, p in enumerate(participants, start=1):
        if p.pk == participant.pk:
            position = idx
            break

    finished_count = participants_qs.filter(is_finished=True).count()
    avg_score = participants_qs.aggregate(avg=Avg('score'))['avg']

    context = {
        'participant': participant,
        'session': session,
        'game_task': game_task,
        'position': position,
        'total_participants': total,
        'finished_count': finished_count,
        'avg_score': avg_score,
    }
    return render(request, 'app/main/gameplay/result/page.html', context)


# gameplay_finish_action
# ----------------------------------------------------------------------------------------------------------------------
def gameplay_finish_action(request, token):
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    participant = get_object_or_404(
        Participant.objects.select_related('session'),
        token=token,
    )
    session = participant.session
    if session.is_pending():
        return redirect('main:gameplay_waiting', token=token)

    if not participant.is_finished:
        participant.is_finished = True
        participant.finished_at = timezone.now()
        participant.save(update_fields=['is_finished', 'finished_at'])

    return redirect('main:gameplay_result', token=token)
