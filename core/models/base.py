from django.db import models
from django.utils.translation import gettext_lazy as _

# -------------- TimeStampedModel --------------
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now=True)

    class Meta:
        abstract = True


# -------------- ActiveModel --------------
class ActiveModel(models.Model):
    is_active = models.BooleanField(_('Is active'), default=True)

    class Meta:
        abstract = True


# -------------- BaseModel --------------
class BaseModel(TimeStampedModel, ActiveModel):
    class Meta:
        abstract = True
