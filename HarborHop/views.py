from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import UserRegistrationForm, BookingForm
from .models import Route, Schedule, Booking, Vessel, Port
from social_django.utils import load_strategy
from django.http import JsonResponse
from decimal import Decimal
from django.utils import timezone
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

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
    if request.user.is_authenticated:
        return redirect('home')
    
    next_url = request.GET.get('next', 'home')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, "You have successfully logged in!")
                return redirect(next_url)
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

@login_required
def checkout(request):
    if request.method == 'POST':
        try:
            # Get booking data from session
            booking_data = request.session.get('booking_data', {})
            if not booking_data:
                messages.error(request, 'No booking data found')
                return redirect('home')

            schedule_id = booking_data.get('schedule_id')
            if not schedule_id:
                messages.error(request, 'No schedule selected')
                return redirect('home')

            # Get schedule instance
            schedule = get_object_or_404(Schedule, id=schedule_id)
            
            # Calculate taxes and total amount
            base_price = Decimal(booking_data['base_price'])
            number_of_passengers = int(booking_data['number_of_passengers'])
            base_fare = base_price * number_of_passengers
            taxes = base_fare * Decimal('0.12')
            
            # Create booking
            booking = Booking.objects.create(
                name=booking_data['name'],
                email=booking_data['email'],
                phone_number=booking_data['phone_number'],
                gender=booking_data['gender'],
                age=int(booking_data['age']),
                package_type=booking_data['package_type'],
                number_of_passengers=number_of_passengers,
                base_price=base_price,
                base_fare=base_fare,
                taxes=taxes,
                schedule=schedule
            )
            
            # Update available seats
            schedule.available_seats -= number_of_passengers
            schedule.save()
            
            # Clear session data
            del request.session['booking_data']
            
            messages.success(request, 'Booking created successfully!')
            return redirect('booking_list')
            
        except Exception as e:
            print("Error:", str(e))  # Debug print
            messages.error(request, f'Error creating booking: {str(e)}')
            return redirect('payment')
    
    return redirect('payment')

def about(request):
    return render(request, 'HarborHop/about.html')

@login_required
def account(request):
    user = request.user
    social_accounts = user.social_auth.all() if hasattr(user, 'social_auth') else []
    context = {
        'user': user,
        'social_accounts': social_accounts,
    }
    return render(request, 'HarborHop/account.html', context)

@login_required
def booking_list(request):
    bookings = Booking.objects.filter(email=request.user.email).order_by('-created_at')
    return render(request, 'HarborHop/booking_list.html', {'bookings': bookings})

@login_required
def booking_create(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.save()
            return redirect('booking_list')
    else:
        form = BookingForm()
    
    context = {
        'form': form,
        'popular_routes': Route.objects.filter(is_active=True)[:5]
    }
    return render(request, 'HarborHop/booking_create.html', context)

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
    return render(request, 'HarborHop/booking_update.html', {'form': form})

@login_required
def booking_delete(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    if request.method == 'POST':
        schedule = booking.schedule
        schedule.available_seats += booking.number_of_passengers
        schedule.save()
        booking.delete()
        return redirect('booking_list')
    return render(request, 'HarborHop/booking_delete.html', {'booking': booking})

@login_required
def profile_update(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('account')
    
    return render(request, 'HarborHop/profile_update.html')

# API endpoints for dynamic booking
def get_available_routes(request):
    routes = Route.objects.filter(is_active=True).values(
        'id', 'departure_port__name', 'arrival_port__name', 
        'base_price', 'duration'
    )
    return JsonResponse(list(routes), safe=False)

def get_available_schedules(request):
    try:
        route_id = request.GET.get('route')
        date = request.GET.get('date')
        
        if not route_id or not date:
            return JsonResponse({'error': 'Missing route_id or date'}, status=400)
        
        # Convert date string to datetime objects for range query
        from datetime import datetime
        from django.utils import timezone
        import pytz

        # Parse the date and create datetime range
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        start_datetime = timezone.make_aware(datetime.combine(date_obj, datetime.min.time()))
        end_datetime = timezone.make_aware(datetime.combine(date_obj, datetime.max.time()))
        
        # Query schedules
        schedules = Schedule.objects.filter(
            route_id=route_id,
            departure_time__range=(start_datetime, end_datetime),
            available_seats__gt=0,
            status='SCHEDULED'
        ).values(
            'id',
            'departure_time',
            'arrival_time',
            'available_seats',
            'vessel__name'
        )
        
        # Convert to list and format datetime
        schedule_list = list(schedules)
        for schedule in schedule_list:
            schedule['departure_time'] = schedule['departure_time'].strftime('%Y-%m-%d %H:%M:%S')
            schedule['arrival_time'] = schedule['arrival_time'].strftime('%Y-%m-%d %H:%M:%S')
        
        return JsonResponse(schedule_list, safe=False)
        
    except Exception as e:
        print(f"Error in get_available_schedules: {str(e)}")  # Debug print
        return JsonResponse({'error': str(e)}, status=500)

def calculate_fare(request):
    schedule_id = request.GET.get('schedule')
    passengers = int(request.GET.get('passengers', 1))
    
    schedule = get_object_or_404(Schedule, id=schedule_id)
    base_fare = schedule.route.base_price * passengers
    taxes = base_fare * Decimal('0.12')  # 12% tax
    total = base_fare + taxes
    
    return JsonResponse({
        'base_fare': str(base_fare),
        'taxes': str(taxes),
        'total': str(total)
    })

# Route Management Views
@user_passes_test(lambda u: u.is_staff)
def route_list(request):
    routes = Route.objects.all().order_by('departure_port__name')
    return render(request, 'HarborHop/route_list.html', {'routes': routes})

@user_passes_test(lambda u: u.is_staff)
def route_create(request):
    if request.method == 'POST':
        # Handle route creation
        departure_port = get_object_or_404(Port, id=request.POST.get('departure_port'))
        arrival_port = get_object_or_404(Port, id=request.POST.get('arrival_port'))
        route = Route.objects.create(
            departure_port=departure_port,
            arrival_port=arrival_port,
            base_price=request.POST.get('base_price'),
            distance=request.POST.get('distance'),
            duration=request.POST.get('duration'),
            is_active=True
        )
        return redirect('route_list')
    return render(request, 'HarborHop/route_form.html')

@user_passes_test(lambda u: u.is_staff)
def route_update(request, pk):
    route = get_object_or_404(Route, pk=pk)
    if request.method == 'POST':
        # Handle route update
        route.departure_port = get_object_or_404(Port, id=request.POST.get('departure_port'))
        route.arrival_port = get_object_or_404(Port, id=request.POST.get('arrival_port'))
        route.base_price = request.POST.get('base_price')
        route.distance = request.POST.get('distance')
        route.duration = request.POST.get('duration')
        route.is_active = request.POST.get('is_active', False) == 'on'
        route.save()
        return redirect('route_list')
    return render(request, 'HarborHop/route_form.html', {'route': route})

@user_passes_test(lambda u: u.is_staff)
def route_delete(request, pk):
    route = get_object_or_404(Route, pk=pk)
    if request.method == 'POST':
        route.delete()
        return redirect('route_list')
    return render(request, 'HarborHop/route_delete.html', {'route': route})

# Schedule Management Views
@user_passes_test(lambda u: u.is_staff)
def schedule_list(request):
    schedules = Schedule.objects.all().order_by('departure_time')
    return render(request, 'HarborHop/schedule_list.html', {'schedules': schedules})

@user_passes_test(lambda u: u.is_staff)
def schedule_create(request):
    if request.method == 'POST':
        # Handle schedule creation
        route = get_object_or_404(Route, id=request.POST.get('route'))
        vessel = get_object_or_404(Vessel, id=request.POST.get('vessel'))
        schedule = Schedule.objects.create(
            route=route,
            vessel=vessel,
            departure_time=request.POST.get('departure_time'),
            arrival_time=request.POST.get('arrival_time'),
            available_seats=vessel.seating_capacity,
            status='SCHEDULED'
        )
        return redirect('schedule_list')
    routes = Route.objects.filter(is_active=True)
    vessels = Vessel.objects.all()
    return render(request, 'HarborHop/schedule_form.html', {
        'routes': routes,
        'vessels': vessels
    })

@user_passes_test(lambda u: u.is_staff)
def schedule_update(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    if request.method == 'POST':
        # Handle schedule update
        schedule.route = get_object_or_404(Route, id=request.POST.get('route'))
        schedule.vessel = get_object_or_404(Vessel, id=request.POST.get('vessel'))
        schedule.departure_time = request.POST.get('departure_time')
        schedule.arrival_time = request.POST.get('arrival_time')
        schedule.status = request.POST.get('status')
        schedule.save()
        return redirect('schedule_list')
    routes = Route.objects.filter(is_active=True)
    vessels = Vessel.objects.all()
    return render(request, 'HarborHop/schedule_form.html', {
        'schedule': schedule,
        'routes': routes,
        'vessels': vessels
    })

@user_passes_test(lambda u: u.is_staff)
def schedule_delete(request, pk):
    schedule = get_object_or_404(Schedule, pk=pk)
    if request.method == 'POST':
        schedule.delete()
        return redirect('schedule_list')
    return render(request, 'HarborHop/schedule_delete.html', {'schedule': schedule})

# Destination Booking Views
def booking_boracay(request):
    try:
        # Get all active routes
        active_routes = Route.objects.filter(is_active=True)
        print("Active routes:", active_routes)  # Debug print
        
        # Get routes with Boracay/Caticlan
        boracay_routes = Route.objects.filter(
            Q(arrival_port__name__icontains='Boracay') |
            Q(arrival_port__name__icontains='Caticlan'),
            is_active=True
        )
        print("Boracay routes:", boracay_routes)  # Debug print
        
        boracay_route = boracay_routes.first()
        if not boracay_route:
            messages.error(request, 'Boracay route is currently unavailable. Please create route data first.')
            return render(request, 'HarborHop/booking_error.html', {
                'error': 'No active route to Boracay found',
                'debug_info': {
                    'active_routes': list(active_routes),
                    'boracay_routes': list(boracay_routes),
                }
            })
        
        # Rest of your existing code...
        if not boracay_route:
            messages.error(request, 'Boracay route is currently unavailable')
            return redirect('home')
        
        # Get future schedules for today and upcoming dates
        today = timezone.now()
        initial_schedules = Schedule.objects.filter(
            route=boracay_route,
            departure_time__gte=today,
            status='SCHEDULED',
            available_seats__gt=0
        ).order_by('departure_time')[:5]
        
        context = {
            'route': boracay_route,
            'initial_schedules': initial_schedules,
            'min_date': today.date().isoformat(),
            'max_date': (today + timezone.timedelta(days=90)).date().isoformat()
        }
        return render(request, 'HarborHop/booking_boracay.html', context)
        
    except Exception as e:
        print(f"Error in booking_boracay: {str(e)}")  # Debug print
        messages.error(request, 'An error occurred while loading the booking page')
        return redirect('home')

def booking_cebu(request):
    try:
        today = timezone.now()
        context = {
            'min_date': today.date().isoformat(),
            'max_date': (today + timezone.timedelta(days=90)).date().isoformat()
        }
        return render(request, 'HarborHop/booking_cebu.html', context)
    except Exception as e:
        print(f"Error in booking_cebu: {str(e)}")  # Debug print
        messages.error(request, 'An error occurred while loading the booking page')
        return redirect('home')

def booking_elnido(request):
    return render(request, 'HarborHop/booking_elnido.html')

def booking_siargao(request):
    return render(request, 'HarborHop/booking_siargao.html')

@login_required
def payment(request):
    if request.method == 'POST':
        try:
            # Get schedule instance
            schedule_id = request.POST.get('schedule_id')
            if not schedule_id:
                messages.error(request, 'No schedule selected')
                return redirect('booking_boracay')

            schedule = get_object_or_404(Schedule, id=schedule_id)
            passengers = int(request.POST.get('passengers', 1))
            
            if schedule.available_seats < passengers:
                messages.error(request, 'Not enough seats available')
                return redirect('booking_boracay')

            # Prepare booking data for session
            booking_data = {
                'schedule_id': schedule_id,
                'name': request.POST.get('name'),
                'email': request.POST.get('email'),
                'phone_number': request.POST.get('phone_number'),
                'gender': request.POST.get('gender'),
                'age': request.POST.get('age'),
                'package_type': request.POST.get('package_type'),
                'base_price': request.POST.get('base_price'),
                'number_of_passengers': passengers,
                'travel_date': request.POST.get('travel_date'),
                'departure_time': request.POST.get('departure_time')
            }

            # Store in session
            request.session['booking_data'] = booking_data
            
            # Calculate totals
            base_price = Decimal(booking_data['base_price'])
            base_fare = base_price * passengers
            taxes = base_fare * Decimal('0.12')  # 12% tax
            total = base_fare + taxes
            
            context = {
                **booking_data,
                'base_fare': base_fare,
                'taxes': taxes,
                'total_amount': total,
                'schedule': schedule
            }
            
            return render(request, 'HarborHop/payment.html', context)
            
        except Exception as e:
            print(f"Error in payment view: {str(e)}")  # Debug print
            messages.error(request, f'Error processing payment: {str(e)}')
            return redirect('booking_boracay')
    
    return redirect('home')
