from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'HarborHop/home.html')

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'HarborHop/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'HarborHop/login.html', {'error': 'Invalid login credentials'})
    else:
        return render(request, 'HarborHop/login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def main_home(request):
    return render(request, 'HarborHop/main_home.html')