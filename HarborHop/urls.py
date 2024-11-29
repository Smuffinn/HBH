from django.urls import path
from .views import register, user_login, user_logout, home, checkout, about, account 
from .views import booking_create, booking_delete, booking_update, booking_list

urlpatterns = [
    path('', home, name='home'),
    
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('checkout/', checkout, name='checkout'),
    path('about/', about, name='about'),
    path('account/', account, name='account'),

    path('booking/', booking_create, name='booking_create'),
    path('booking_list/', booking_list, name='booking_list'),
    path('update/<int:pk>/', booking_update, name='booking_update'),
    path('delete/<int:pk>/', booking_delete, name='booking_delete'),  
]