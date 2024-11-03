from django.shortcuts import render, redirect
from .forms import PassengerForm
from .models import Passenger

def add_passenger(request):
    num_additional_passengers = 0
    additional_passengers_range = []

    if request.method == 'POST':
        # Get the number of additional passengers from the form
        num_additional_passengers = int(request.POST.get('num_additional_passengers', 0))
        form = PassengerForm(request.POST)
        
        if form.is_valid():
            # Save the primary passenger
            passenger = form.save(commit=False)
            if passenger.class_type == 'economy':
                passenger.price = 100.00  # Set price for economy
            elif passenger.class_type == 'first':
                passenger.price = 200.00  # Set price for first class
            
            passenger.save()

            # Save additional passengers
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
                
                # Set the price based on class type for additional passengers
                if additional_passenger.class_type == 'economy':
                    additional_passenger.price = 100.00
                elif additional_passenger.class_type == 'first':
                    additional_passenger.price = 200.00
                
                # Check for required fields
                if not additional_passenger.name:  # Check if the name field is filled
                    continue  # Skip saving this passenger if the name is missing

                additional_passenger.save()

            return redirect('checkout')  # Redirect to checkout page after saving

    else:
        form = PassengerForm()
    
    # Create a range object to iterate over in the template for additional passengers
    additional_passengers_range = range(1, num_additional_passengers + 1)

    return render(request, 'booking_flow/add_passenger.html', {
        'form': form,
        'num_additional_passengers': num_additional_passengers,
        'additional_passengers_range': additional_passengers_range
    })

def checkout(request):
    passengers = Passenger.objects.all()  # Get all passengers for checkout
    return render(request, 'booking_flow/checkout.html', {'passengers': passengers})

def home(request):
    return render(request, 'booking_flow/home.html')

from django.shortcuts import render

def about(request):
    return render(request, 'booking_flow/about.html')

