# views.py
from django.http import JsonResponse
from django.shortcuts import render,redirect
from django.views import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from .models import Vendor
from .serializers import VendorSerializer, UserSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.contrib.auth import authenticate,login
from rest_framework_simplejwt.authentication import JWTAuthentication
import json
from rest_framework_simplejwt.tokens import RefreshToken




class VendorDashboardView(View):
    authentication_classes = [JWTAuthentication]  # JWT Authentication
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request):
        # If JWT authentication is successful, the user is authenticated
        if not hasattr(request.user, 'vendor_profile'):
            return JsonResponse({'message': 'Unauthorized'}, status=403)

        try:
            vendor = Vendor.objects.get(user=request.user)  # Get the vendor profile
            return render(request, 'dashboard.html', {'vendor': vendor})  # Render dashboard
        except Vendor.DoesNotExist:
            return JsonResponse({'message': 'Vendor profile not found'}, status=404)
 
    



from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from .models import Vendor

class RegisterVendorView(View):
    def get(self, request):
        # Render the registration form
        return render(request, 'register.html')

    def post(self, request):
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
        return redirect('vendor_login')  # Redirect to the login page (use the correct URL name)

class VendorLoginView(View):
    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user and hasattr(user, 'vendor_profile'):  # Ensure it's a vendor
            login(request, user)
            # Generate tokens if needed for other purposes
            self.generate_tokens(user)  # Tokens are not returned but can be stored or logged if necessary
            return redirect('/vendor/dashboard/')  # Redirect to dashboard on success

        error_message = 'Invalid credentials or not a vendor.'
        return render(request, 'login.html', {'error': error_message})

    @staticmethod
    def generate_tokens(user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import View

class VendorLogoutView(View):
    def get(self, request, *args, **kwargs):
        logout(request)  # Logs the user out
        return redirect('vendor_login')  # Redirects to the login page (ensure 'login' matches your URL pattern name)
