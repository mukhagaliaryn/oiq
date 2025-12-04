from django.db import models
import uuid
import random
import string
from datetime import timedelta
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


# GameTask
# ----------------------------------------------------------------------------------------------------------------------
# GameTask model
class GameTask(models.Model):
    STATUS = (
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('archived', _('Archived')),
    )
    name = models.CharField(_('Name'), max_length=128)
    owner = models.ForeignKey(
        'core.User', on_delete=models.CASCADE,
        related_name='game_tasks', verbose_name=_('Owner')
    )
    subject = models.ForeignKey(
        'core.Subject', on_delete=models.CASCADE, null=True, blank=True,
        related_name='game_tasks', verbose_name=_('Subject')
    )
    activity = models.ForeignKey(
        'core.Activity', on_delete=models.CASCADE, null=True, blank=True,
        related_name='game_tasks', verbose_name=_('Activity')
    )
    status = models.CharField(_('Status'), max_length=16, choices=STATUS, default='draft')
    description = models.TextField(_('Description'), null=True, blank=True)

    class Meta:
        verbose_name = _('Game Task')
        verbose_name_plural = _('Game Tasks')

    def __str__(self):
        return self.name


# GameTaskQuestion
class GameTaskQuestion(models.Model):
    game_task = models.ForeignKey(
        GameTask, on_delete=models.CASCADE,
        related_name='questions', verbose_name=_('Game Task')
    )
    question = models.ForeignKey(
        'core.Question', on_delete=models.CASCADE,
        related_name='questions', verbose_name=_('Question')
    )
    order = models.PositiveSmallIntegerField(_('Order'), default=0)

    class Meta:
        verbose_name = _('Game Task Question')
        verbose_name_plural = _('Game Task Questions')

    def __str__(self):
        return f'{self.game_task}: {self.order}-{self.question}'


# GameTaskSession model
def generate_pin_code(length: int = 6) -> str:
    digits = string.digits
    return ''.join(random.choice(digits) for _ in range(length))


class GameTaskSession(models.Model):
    STATUS = (
        ('pending', _('Pending')),
        ('active', _('Active')),
        ('finished', _('Finished')),
    )

    game_task = models.ForeignKey(
        GameTask, on_delete=models.CASCADE,
        related_name='sessions', verbose_name=_('Game Task')
    )
    status = models.CharField(_('Status'), max_length=16, choices=STATUS, default='pending')
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    duration = models.PositiveIntegerField(_('Duration (minutes)'), default=0)
    pin_code = models.CharField(_('PIN code'), max_length=8, editable=False, unique=True, null=True)

    class Meta:
        verbose_name = _('Game Task Session')
        verbose_name_plural = _('Game Task Sessions')

    def __str__(self):
        return f'{self.game_task} ({self.status})'

    @property
    def deadline(self):
        if self.started_at and self.duration:
            return self.started_at + timedelta(minutes=self.duration)
        return None

    def is_time_over(self) -> bool:
        dl = self.deadline
        if not dl:
            return False
        return timezone.now() >= dl

    def is_pending(self) -> bool:
        return self.status == 'pending'

    def is_active(self) -> bool:
        return self.status == 'active'

    def is_finished(self) -> bool:
        return self.status == 'finished'

    def is_joinable(self) -> bool:
        return self.is_pending()

    def _ensure_pin_code(self):
        if self.pin_code:
            return

        while True:
            candidate = generate_pin_code()
            if not GameTaskSession.objects.filter(pin_code=candidate).exists():
                self.pin_code = candidate
                break

    def save(self, *args, **kwargs):
        if not self.pk and not self.pin_code:
            self._ensure_pin_code()
        super().save(*args, **kwargs)


# Participant model
class Participant(models.Model):
    session = models.ForeignKey(
        GameTaskSession, on_delete=models.CASCADE,
        related_name='participants', verbose_name=_('Game Task Session')
    )
    nickname = models.CharField(_('Nickname'), max_length=128)
    token = models.UUIDField(_('Token'), default=uuid.uuid4, unique=True)
    score = models.IntegerField(_('Score'), default=0)
    correct_count = models.PositiveIntegerField(_('Correct answers'), default=0)
    started_at = models.DateTimeField(_('Started at'), blank=True, null=True)
    finished_at = models.DateTimeField(_('Finished at'), blank=True, null=True)
    is_finished = models.BooleanField(_('Is finished'), default=False)

    class Meta:
        verbose_name = _('Participant')
        verbose_name_plural = _('Participants')

    def __str__(self):
        return self.nickname or str(self.token)


# QuestionAttempt
class QuestionAttempt(models.Model):
    participant = models.ForeignKey(
        Participant, on_delete=models.CASCADE,
        related_name='attempts', verbose_name=_('Participant')
    )
    question = models.ForeignKey(
        'core.Question', on_delete=models.CASCADE,
        related_name='attempts', verbose_name=_('Question')
    )
    is_correct = models.BooleanField(_('Is correct'), null=True, blank=True)
    score_delta = models.IntegerField(_('Score delta'), default=0)
    time_spent = models.PositiveIntegerField(_('Time spent (seconds)'), default=0)
    answered_at = models.DateTimeField(_('Answered at'), auto_now_add=True)

    class Meta:
        verbose_name = _('Question attempt')
        verbose_name_plural = _('Question attempts')
        constraints = [
            models.UniqueConstraint(
                fields=['participant', 'question'],
                name='unique_participant_question_result'
            )
        ]

    def __str__(self):
        return f'{self.participant} → Q{self.question.pk}'


# Question format: test
# ----------------------------------------------------------------------------------------------------------------------
# TestAnswer model
class TestAnswer(models.Model):
    attempt = models.ForeignKey(
        QuestionAttempt, on_delete=models.CASCADE,
        related_name='test_answers', verbose_name=_('Question attempt')
    )
    selected_options = models.ManyToManyField(
        'core.Option', related_name='answers',
        verbose_name=_('Selected options'), blank=True,
    )

    def __str__(self):
        return f'Test answer for {self.attempt}'


# Question format: matching
# ----------------------------------------------------------------------------------------------------------------------
# ...