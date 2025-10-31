from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from apps.main.forms import UserRegisterForm


# login page
# ----------------------------------------------------------------------------------------------------------------------
def login_view(request):
    if request.user.is_authenticated:
        return redirect('learner_home')

    if request.method == 'POST':
        identifier = request.POST.get('identifier')  # email немесе username
        password = request.POST.get('password')
        user = authenticate(request, username=identifier, password=password)

        if user is not None:
            login(request, user)
            return redirect('learner_home')
        else:
            messages.error(request, _('Incorrect username or password'))
            return render(request, 'app/auth/login/page.html', {'identifier': identifier})

    return render(request, 'app/auth/login/page.html')


# register page
# ----------------------------------------------------------------------------------------------------------------------
def register_view(request):
    if request.user.is_authenticated:
        return redirect('learner_home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, _('You have successfully registered!'))
            return redirect('learner_home')
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
