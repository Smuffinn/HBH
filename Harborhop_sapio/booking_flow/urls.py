from django.urls import path
from .views import add_passenger, checkout, home, about

urlpatterns = [
    path('', home, name='home'),  # This root path should render the home view
    path('add-passenger/', add_passenger, name='add_passenger'),
    path('checkout/', checkout, name='checkout'),
    path('about/', about, name='about'),
]
