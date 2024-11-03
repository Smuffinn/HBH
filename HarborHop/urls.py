from django.urls import path
from .views import register, user_login, user_logout, home, main_home, add_passenger, checkout, about

urlpatterns = [
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('main_home/', main_home, name='main_home'),
    path('add-passenger/', add_passenger, name='add_passenger'),
    path('checkout/', checkout, name='checkout'),
    path('about/', about, name='about'),
]