from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from apps.main.forms import UserRegisterForm


# login page
# ----------------------------------------------------------------------------------------------------------------------
def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next')
    if request.user.is_authenticated:
        if next_url:
            return redirect(f"{reverse('dashboard:dashboard')}?next={next_url}")
        return redirect('dashboard:dashboard')

    if request.method == 'POST':
        identifier = request.POST.get('identifier')
        password = request.POST.get('password')
        user = authenticate(request, username=identifier, password=password)

        if user is not None:
            login(request, user)
            if next_url:
                return redirect(f"{reverse('dashboard:dashboard')}?next={next_url}")
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, _('Incorrect username or password'))
            return render(request, 'app/main/auth/login/page.html', {'identifier': identifier})

    return render(request, 'app/main/auth/login/page.html')


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
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, _('Registration failed. Check the data!'))
    else:
        form = UserRegisterForm()

    context = {
        'form': form
    }
    return render(request, 'app/main/auth/register/page.html', context)


# logout action
# ----------------------------------------------------------------------------------------------------------------------
def logout_view(request):
    logout(request)
    return redirect('main:login')

