from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.translation import gettext_lazy as _
from apps.main.forms import UserRegisterForm


# post_login_redirect
# ----------------------------------------------------------------------------------------------------------------------
ROLE_REDIRECTS = {
    'learner': 'learner_dashboard',
    'teacher': 'teacher:dashboard',
    'admin':   'admin:index',
}

def post_login_redirect(request):
    user = request.user
    role = getattr(user, 'user_role', 'learner')
    default_url = reverse(ROLE_REDIRECTS.get(role, 'learner_dashboard'))

    next_url = request.GET.get('next') or request.POST.get('next')
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        role_prefix = {
            'learner': f'/learner/',
            'teacher': f'/teacher/',
            'admin':   f'/admin/',
        }.get(role)

        if role_prefix and next_url.startswith(role_prefix):
            return redirect(next_url)
    return redirect(default_url)


# login page
# ----------------------------------------------------------------------------------------------------------------------
def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next')

    if request.user.is_authenticated:
        if next_url:
            return redirect(f'{reverse('post_login_redirect')}?next={next_url}')
        return redirect('post_login_redirect')

    if request.method == 'POST':
        identifier = request.POST.get('identifier')  # email немесе username
        password = request.POST.get('password')
        user = authenticate(request, username=identifier, password=password)

        if user is not None:
            login(request, user)
            if next_url:
                return redirect(f'{reverse('post_login_redirect')}?next={next_url}')
            return redirect('post_login_redirect')
        else:
            messages.error(request, _('Incorrect username or password'))
            return render(request, 'app/auth/login/page.html', {'identifier': identifier})

    return render(request, 'app/auth/login/page.html')


# register page
# ----------------------------------------------------------------------------------------------------------------------
def register_view(request):
    if request.user.is_authenticated:
        return redirect('post_login_redirect')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, _('You have successfully registered!'))
            return redirect('post_login_redirect')
        else:
            messages.error(request, _('Registration failed. Check the data!'))
    else:
        form = UserRegisterForm()

    context = {
        'form': form
    }
    return render(request, 'app/auth/register/page.html', context)



# logout control
# ----------------------------------------------------------------------------------------------------------------------
def logout_view(request):
    logout(request)
    return redirect('login')

