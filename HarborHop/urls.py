from django.urls import path
from django.contrib.auth import views as auth_views
from .views import (
    # Authentication views
    register, user_login, user_logout, profile_update,
    
    # Main page views
    home, checkout, about, account,
    
    # Booking views
    booking_create, booking_delete, booking_update, booking_list,
    
    # Route management views
    route_list, route_create, route_update, route_delete,
    
    # Schedule management views
    schedule_list, schedule_create, schedule_update, schedule_delete,
    
    # API endpoints
    get_available_routes, get_available_schedules, calculate_fare, get_available_ports,
    
    # Destination booking views
    booking_boracay, booking_cebu, booking_elnido, booking_siargao,
    
    # Add payment view to imports
    payment,
)

urlpatterns = [
    # Move booking routes to the top
    path('booking/boracay/', booking_boracay, name='booking_boracay'),
    path('booking/cebu/', booking_cebu, name='booking_cebu'),
    path('booking/elnido/', booking_elnido, name='booking_elnido'),
    path('booking/siargao/', booking_siargao, name='booking_siargao'),
    path('payment/', payment, name='payment'),

    path('', home, name='home'),
    
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('checkout/', checkout, name='checkout'),
    path('about/', about, name='about'),
    path('account/', account, name='account'),

    path('booking/', booking_create, name='booking_create'),
    path('booking/list/', booking_list, name='booking_list'),
    path('update/<int:pk>/', booking_update, name='booking_update'),
    path('delete/<int:pk>/', booking_delete, name='booking_delete'),

    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='HarborHop/password_change.html',
        success_url='/account/password_change/done/'),
        name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='HarborHop/password_change_done.html'),
        name='password_change_done'),
    path('profile/update/', profile_update, name='profile_update'),

    # Route Management
    path('routes/', route_list, name='route_list'),
    path('route/create/', route_create, name='route_create'),
    path('route/<int:pk>/update/', route_update, name='route_update'),
    path('route/<int:pk>/delete/', route_delete, name='route_delete'),
    
    # Schedule Management
    path('schedules/', schedule_list, name='schedule_list'),
    path('schedule/create/', schedule_create, name='schedule_create'),
    path('schedule/<int:pk>/update/', schedule_update, name='schedule_update'),
    path('schedule/<int:pk>/delete/', schedule_delete, name='schedule_delete'),
    
    # API Endpoints for Dynamic Booking
    path('api/routes/available/', get_available_routes, name='api_available_routes'),
    path('api/schedules/available/', get_available_schedules, name='api_available_schedules'),
    path('api/calculate-fare/', calculate_fare, name='api_calculate_fare'),
    path('api/ports/available/<int:departure_id>/', get_available_ports, name='api_available_ports'),
]