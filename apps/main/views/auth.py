from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.main.forms.auth import LearnerRegisterForm
from apps.main.forms.auth import LoginForm
from apps.main.forms.auth import TeacherRegisterForm
from apps.main.services.auth import create_learner_user
from apps.main.services.auth import create_teacher_user
from apps.main.services.auth import get_user_redirect_url
from apps.main.services.email import send_registration_success_email
from apps.main.services.sessions import save_user_session
from core.utils.decorators import anonymous_required


# -------------- login view --------------
@anonymous_required
def login_view(request):
    form = LoginForm(request=request, data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            save_user_session(request, user)
            messages.success(request, _('You have successfully signed in.'))
            return redirect(get_user_redirect_url(user))

        for error in form.non_field_errors():
            messages.error(request, error)

    context = {
        'form': form,
    }
    return render(request, 'app/auth/login/page.html', context)


# -------------- logout view --------------
def logout_view(request):
    logout(request)
    messages.success(request, _('You have been signed out.'))
    return redirect('main:login')


# register
# ----------------------------------------------------------------------------------------------------------------------
# -------------- register select --------------
@anonymous_required
def register_select_view(request):
    return render(request,'app/auth/register/page.html')


# -------------- learner register --------------
@anonymous_required
def learner_register_view(request):
    form = LearnerRegisterForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = create_learner_user(form=form)

            # Email activation кейін қосамыз.
            user.is_active = True
            user.save(update_fields=['is_active'])
            send_registration_success_email(user)

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            save_user_session(request, user)
            messages.success(request, _('Your account has been created successfully.'))
            return redirect(f'{get_user_redirect_url(user)}?clear_register=1')

        for error in form.non_field_errors():
            messages.error(request, error)

    context = {
        'form': form,
    }
    return render(request,'app/auth/register/learner.html', context)


# -------------- teacher register --------------
@anonymous_required
def teacher_register_view(request):
    form = TeacherRegisterForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            user = create_teacher_user(
                form=form,
                agreement_accepted_at=timezone.now(),
            )

            # Email activation кейін қосамыз.
            user.is_active = True
            user.save(update_fields=['is_active'])
            send_registration_success_email(user)

            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            save_user_session(request, user)
            messages.success(request, _('Teacher account has been created successfully.'))
            return redirect(f'{get_user_redirect_url(user)}?clear_register=1')

        for error in form.non_field_errors():
            messages.error(request, error)

    context = {
        'form': form,
    }
    return render(request, 'app/auth/register/teacher.html', context)