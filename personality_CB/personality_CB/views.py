from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import SignUpForm, LoginForm
from django.contrib import messages
from django.contrib.auth.models import auth

def auth_view(request):
    signup_form = SignUpForm()
    login_form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST':
        if 'signup' in request.POST:
            signup_form = SignUpForm(request.POST)
            if signup_form.is_valid():
                user = signup_form.save(commit=False)
                user.set_password(signup_form.cleaned_data['password'])
                user.save()
                messages.success(request, "Signup successful. You can now log in.")
                return redirect('auth')
        elif 'login' in request.POST:
            login_form = LoginForm(request, data=request.POST)
            if login_form.is_valid():
                user = authenticate(
                    request, 
                    username=login_form.cleaned_data['username'], 
                    password=login_form.cleaned_data['password']
                )
                if user is not None:
                    login(request, user)
                    return redirect('/home/')  # change to your desired page
                else:
                    messages.error(request, "Invalid login credentials.")

    return render(request, 'auth.html', {
        'signup_form': signup_form,
        'login_form': login_form
    })


def logout(request):
    auth.logout(request)
    return redirect('/') 