from django.db.models import Q
from apps.accounts.models import User


def get_active_students():
    return User.objects.filter(account_type=User.AccountType.LEARNER, is_active=True)


# -------------- get_teacher_by_username --------------
def get_teacher_by_username(username):
    return User.objects.filter(
        username=username, account_type=User.AccountType.TEACHER, is_active=True,
    ).first()


# -------------- get_user --------------
def get_user(user_id):
    if not user_id:
        return None

    return User.objects.filter(pk=user_id, is_active=True).first()


# -------------- find_users --------------
def find_users(query):
    if not query:
        return User.objects.none()

    return User.objects.filter(
        Q(email__icontains=query)
        | Q(username__icontains=query)
        | Q(phone__icontains=query)
        | Q(first_name__icontains=query)
        | Q(last_name__icontains=query),
        is_active=True,
    )[:10]
