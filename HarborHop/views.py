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
import datetime

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
            booking.user = request.user
            booking.save()
            return redirect('payment')
    
    context = {
        'ports': Port.objects.filter(is_active=True),  # Add is_active filter back
        'routes': Route.objects.filter(is_active=True).values('id', 'departure_port__name', 'arrival_port__name', 'base_price', 'duration'),
        'min_date': timezone.now().date().isoformat(),
        'max_date': (timezone.now() + timezone.timedelta(days=90)).date().isoformat()
    }
    return render(request, 'HarborHop/booking_create.html', context)

def get_available_ports(request, departure_id):
    departure_port = get_object_or_404(Port, id=departure_id)
    available_ports = Port.objects.filter(
        arrival_routes__departure_port=departure_port,
        is_active=True
    ).distinct()
    return JsonResponse(list(available_ports.values('id', 'name')), safe=False)

def get_available_schedules(request):
    try:
        route_id = request.GET.get('route')
        departure_id = request.GET.get('departure')
        arrival_id = request.GET.get('arrival')
        date = request.GET.get('date')
        
        if not date:
            return JsonResponse({'error': 'Date is required'}, status=400)
            
        # Parse the date string to datetime
        date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
        start_datetime = timezone.make_aware(datetime.datetime.combine(date_obj, datetime.time.min))
        end_datetime = timezone.make_aware(datetime.datetime.combine(date_obj, datetime.time.max))

        # Find the route based on either route_id or departure/arrival ports
        if route_id:
            route = get_object_or_404(Route, id=route_id, is_active=True)
        elif departure_id and arrival_id:
            route = Route.objects.filter(
                departure_port_id=departure_id,
                arrival_port_id=arrival_id,
                is_active=True
            ).first()
        else:
            return JsonResponse({'error': 'Invalid route parameters'}, status=400)

        if not route:
            return JsonResponse({'error': 'No active route found'}, status=404)

        # Query schedules
        schedules = Schedule.objects.select_related('vessel', 'route').filter(
            route=route,
            departure_time__range=(start_datetime, end_datetime),
            available_seats__gt=0,
            status='SCHEDULED'
        ).order_by('departure_time')
        
        schedule_list = [{
            'id': schedule.id,
            'departure_time': schedule.departure_time.isoformat(),
            'arrival_time': schedule.arrival_time.isoformat(),
            'available_seats': schedule.available_seats,
            'vessel__name': schedule.vessel.name,
            'base_price': str(schedule.route.base_price),
            'route_name': f"{schedule.route.departure_port.name} → {schedule.route.arrival_port.name}"
        } for schedule in schedules]
        
        return JsonResponse(schedule_list, safe=False)
        
    except Exception as e:
        logger.error(f"Error in get_available_schedules: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

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
@login_required
def booking_boracay(request):
    try:
        boracay_route = Route.objects.filter(
            Q(arrival_port__name__icontains='Boracay') | Q(departure_port__name__icontains='Boracay'),
            is_active=True
        ).first()

        if not boracay_route:
            messages.error(request, 'Boracay route is currently unavailable')
            return redirect('home')

        context = prepare_booking_context(boracay_route)
        return render(request, 'HarborHop/booking_boracay.html', context)
    except Exception as e:
        messages.error(request, f'Error loading booking page: {str(e)}')
        return redirect('home')

@login_required
def booking_siargao(request):
    try:
        siargao_route = Route.objects.filter(
            Q(arrival_port__name__icontains='Siargao') | Q(departure_port__name__icontains='Siargao'),
            is_active=True
        ).first()

        if not siargao_route:
            messages.error(request, 'Siargao route is currently unavailable')
            return redirect('home')

        context = prepare_booking_context(siargao_route)
        return render(request, 'HarborHop/booking_siargao.html', context)
    except Exception as e:
        messages.error(request, f'Error loading booking page: {str(e)}')
        return redirect('home')

@login_required
def booking_elnido(request):
    try:
        elnido_route = Route.objects.filter(
            Q(arrival_port__name__icontains='El Nido') | Q(departure_port__name__icontains='El Nido'),
            is_active=True
        ).first()

        if not elnido_route:
            messages.error(request, 'El Nido route is currently unavailable')
            return redirect('home')

        context = prepare_booking_context(elnido_route)
        return render(request, 'HarborHop/booking_elnido.html', context)
    except Exception as e:
        messages.error(request, f'Error loading booking page: {str(e)}')
        return redirect('home')

@login_required
def booking_cebu(request):
    try:
        cebu_route = Route.objects.filter(
            Q(arrival_port__name__icontains='Cebu') | Q(departure_port__name__icontains='Cebu'),
            is_active=True
        ).first()

        if not cebu_route:
            messages.error(request, 'Cebu route is currently unavailable')
            return redirect('home')

        context = prepare_booking_context(cebu_route)
        return render(request, 'HarborHop/booking_cebu.html', context)
    except Exception as e:
        messages.error(request, f'Error loading booking page: {str(e)}')
        return redirect('home')

def prepare_booking_context(route):
    """Helper function to prepare context for booking templates"""
    today = timezone.now()
    initial_schedules = Schedule.objects.filter(
        route=route,
        departure_time__gte=today,
        status='SCHEDULED',
        available_seats__gt=0
    ).select_related('vessel').order_by('departure_time')[:5]

    return {
        'route': route,
        'initial_schedules': initial_schedules,
        'min_date': today.date().isoformat(),
        'max_date': (today + timezone.timedelta(days=90)).date().isoformat()
    }

@login_required
def payment(request):
    if request.method == 'POST':
        try:
            # Validate required fields
            required_fields = ['schedule_id', 'name', 'email', 'phone_number', 
                             'gender', 'age', 'passengers', 'base_price']
            
            for field in required_fields:
                if not request.POST.get(field):
                    messages.error(request, f'Missing required field: {field}')
                    return redirect('booking_create')

            schedule = get_object_or_404(Schedule, id=request.POST['schedule_id'])
            passengers = int(request.POST['passengers'])
            base_price = Decimal(request.POST['base_price'])
            
            # Calculate totals
            base_fare = base_price * passengers
            taxes = base_fare * Decimal('0.12')
            total_amount = base_fare + taxes
            
            # Create booking data dictionary with all required fields
            booking_data = {
                'schedule_id': schedule.id,
                'name': request.POST['name'],
                'email': request.POST['email'],
                'phone_number': request.POST['phone_number'],
                'gender': request.POST['gender'],
                'age': int(request.POST['age']),
                'package_type': request.POST.get('package_type', 'regular'),
                'number_of_passengers': passengers,
                'base_price': str(base_price),  # Convert to string
                'travel_date': request.POST.get('travel_date'),
                'departure_time': schedule.departure_time.strftime('%Y-%m-%d %H:%M:%S'),
                'departure_port': schedule.route.departure_port.name,
                'arrival_port': schedule.route.arrival_port.name,
                'vessel_name': schedule.vessel.name,
                'base_fare': str(base_fare),  # Convert to string
                'taxes': str(taxes),  # Convert to string
                'total_amount': str(total_amount)  # Convert to string
            }

            # Store in session
            request.session['booking_data'] = booking_data
            
            # Convert Decimal objects to strings for template context
            context = {
                **booking_data,
                'base_fare_display': f"₱{base_fare:,.2f}",
                'taxes_display': f"₱{taxes:,.2f}",
                'total_amount_display': f"₱{total_amount:,.2f}",
                'schedule': schedule
            }
            
            return render(request, 'HarborHop/payment.html', context)
            
        except Exception as e:
            print(f"Error in payment view: {str(e)}")
            messages.error(request, f'Error processing payment: {str(e)}')
            return redirect('booking_create')
    
    return redirect('booking_create')
