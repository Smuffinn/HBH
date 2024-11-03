from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from .forms import UserRegistrationForm, PassengerForm
from django.contrib.auth.decorators import login_required
from .models import Passenger

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

def add_passenger(request):
    num_additional_passengers = 0
    additional_passengers_range = []

    if request.method == 'POST':
        num_additional_passengers = int(request.POST.get('num_additional_passengers', 0))
        form = PassengerForm(request.POST)
        
        if form.is_valid():
            passenger = form.save(commit=False)
            if passenger.class_type == 'economy':
                passenger.price = 100.00
            elif passenger.class_type == 'first':
                passenger.price = 200.00
            
            passenger.save()

            for i in range(num_additional_passengers):
                additional_passenger = Passenger(
                    name=request.POST.get(f'additional_name_{i + 1}'),
                    gender=request.POST.get(f'additional_gender_{i + 1}'),
                    date_of_birth=request.POST.get(f'additional_date_of_birth_{i + 1}'),
                    address=request.POST.get(f'additional_address_{i + 1}'),
                    email=request.POST.get(f'additional_email_{i + 1}'),
                    phone_number=request.POST.get(f'additional_phone_{i + 1}'),
                    class_type=request.POST.get(f'additional_class_type_{i + 1}'),
                )
                
                if additional_passenger.class_type == 'economy':
                    additional_passenger.price = 100.00
                elif additional_passenger.class_type == 'first':
                    additional_passenger.price = 200.00
                
                if not additional_passenger.name:
                    continue

                additional_passenger.save()

            return redirect('checkout')

    else:
        form = PassengerForm()
    
    additional_passengers_range = range(1, num_additional_passengers + 1)

    return render(request, 'HarborHop/add_passenger.html', {
        'form': form,
        'num_additional_passengers': num_additional_passengers,
        'additional_passengers_range': additional_passengers_range
    })

def checkout(request):
    passengers = Passenger.objects.all()
    return render(request, 'HarborHop/checkout.html', {'passengers': passengers})

def about(request):
    return render(request, 'HarborHop/about.html')