from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Vendor
from django.contrib.auth import authenticate, login, logout
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def register_vendor(request):
    if request.method == 'GET':
        return render(request, 'register.html')  # Render the registration form

    if request.method == 'POST':
        # Handle form submission for registration
        username = request.POST.get('username')
        password = request.POST.get('password')
        business_name = request.POST.get('business_name')
        phone_number = request.POST.get('phone_number')
        email = request.POST.get('email')

        if not all([username, password, business_name, phone_number, email]):
            messages.error(request, 'All fields are required.')
            return render(request, 'register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'register.html')

        # Create user and vendor
        user = User.objects.create_user(username=username, password=password, email=email)
        Vendor.objects.create(user=user, business_name=business_name, phone_number=phone_number, email=email)

        messages.success(request, 'Vendor registered successfully. Please log in.')
        return redirect('vendor_login')


@csrf_exempt
def login_vendor(request):
    if request.method == 'GET':
        return render(request, 'login.html')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user and hasattr(user, 'vendor_profile'):  # Ensure it's a vendor
            login(request, user)
            tokens = generate_tokens(user)  # Generate JWT tokens
            return redirect('vendor_dashboard')

        error_message = 'Invalid credentials or not a vendor.'
        return render(request, 'login.html', {'error': error_message})


def generate_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@login_required(login_url='vendor_login')
def vendor_dashboard(request):
    if not hasattr(request.user, 'vendor_profile'):
        return JsonResponse({'message': 'Unauthorized'}, status=403)

    vendor = Vendor.objects.get(user=request.user)
    return render(request, 'dashboard.html', {'vendor': vendor})


def logout_vendor(request):
    logout(request)  # Logs the user out
    return redirect('vendor_login')  # Redirect to the login page

