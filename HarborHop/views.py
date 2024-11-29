from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
# from .models import Passenger
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Booking
from .forms import BookingForm
def home(request):
    return render(request, 'HarborHop/home.html')

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, 'You are now logged in')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'HarborHop/register.html', {'form': form})

def user_login(request):
    # if request.method == 'POST':
    #     form = AuthenticationForm(request, data=request.POST)
    #     if form.is_valid():
    #         username = form.cleaned_data.get('username')
    #         password = form.cleaned_data.get('password')
    #         user = authenticate(request, username=username, password=password)
    #     if user is not None:
    #         login(request, user)
    #         messages.success(request, 'You are now logged in')
    #         return redirect('home')
    #     else:
    #         return render(request, 'HarborHop/login.html', {'error': 'Invalid login credentials'})
    # else:
    #     return render(request, 'HarborHop/login.html')
    if request.user.is_authenticated:
        return redirect('home') 
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "You have successfully logged in!")
                return redirect('home')  
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid login details. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'HarborHop/login.html', {'form': form})
def user_logout(request):
    logout(request)
    return redirect('home')




def checkout(request):
    bookings = Booking.objects.all()
    return render(request, 'HarborHop/checkout.html', {'bookings': bookings})

def about(request):
    return render(request, 'HarborHop/about.html')




@login_required
def booking_list(request):
    
    bookings = Booking.objects.all()
    return render(request, 'HarborHop/booking_list.html', {'bookings': bookings})

@login_required
def booking_create(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('booking_list')
    else:
        form = BookingForm()
    return render(request, 'HarborHop/booking_create.html', {'form': form})
@login_required
def booking_update(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        form = BookingForm(request.POST, instance=booking)
        if form.is_valid():
            form.save()
            return redirect('booking_list')
    else:
        form = BookingForm(instance=booking)
    return render(request, 'HarborHop/booking_list.html', {'form': form})
@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        booking.delete()
        return redirect('booking_list')
    return render(request, 'HarborHop/booking_confirm_delete.html', {'booking': booking})
