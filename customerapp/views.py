from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .models import Customer, Product, Cart
from django.contrib.auth.decorators import login_required
import requests
from decimal import Decimal
from django.db import transaction
import json
from django.contrib.auth.mixins import LoginRequiredMixin


def generate_jwt_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class CustomerRegisterView(View):
    def get(self, request):
        return render(request, 'cust_register.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        name = request.POST.get('name')
        phone = request.POST.get('phone_number')
        email = request.POST.get('email') 
        referral_code = request.POST.get('referral_code', None)  
        business_name = "Aish Bakers"

        if not username or not password:
            return HttpResponse("Username and password are required.", status=400)

        if User.objects.filter(username=username).exists():
            return HttpResponse("Username already exists.", status=400)
        
        try:
            # with transaction.atomic():        
            user = User.objects.create_user(username=username, password=password, email=email)
            
            customer = Customer.objects.create(
                user=user,
                name=name,
                phone_number=phone,
                email=email,
                referral_code=referral_code
            )

                # response = requests.post(
                #     'http://127.0.0.1:8000/api/customer-data/',  # Adjust URL if necessary
                #     json={
                #         'customer_id': customer.id,
                #         'business1_name': business_name,
                #         'referral_code': referral_code  # This will be None if not provided
                #     }
                # )
                                # Prepare the payload for the API request
            payload = {
                'customer_id': customer.id,
                'business_name': business_name,
                'referral_code': referral_code  # This will be None if not provided
            }

            # Make the API call to send customer data
            response = requests.post(
                'http://127.0.0.1:8000/api/customer-data/',
                json=payload
            )
            print(payload)
        


            if response.status_code != 200:
                # Log the error but do not roll back user creation for signup bonuses
                print(f"Referral API error: {response.status_code}")

        except requests.RequestException as e:
            print(f"API call failed: {str(e)}")
            return HttpResponse("Unable to complete registration. Please try again.", status=500)

        return redirect('cust_login')

class LoginView(View):
    def get(self, request):
        return render(request, 'cust_login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return HttpResponse("Both username and password are required.", status=400)

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return redirect('product-list')

        return HttpResponse("Invalid credentials", status=401)


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('cust_login')


class ProductListView(View):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect('cust_login')

        products = Product.objects.all()
        return render(request, 'products.html', {'products': products})



class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        # Get the product by ID
        product = get_object_or_404(Product, id=product_id)

        # Get the Customer instance linked to the logged-in User
        customer = request.user.customer  # Assumes each User has a related Customer

        # Check if quantity is provided and valid
        quantity = int(request.POST.get('quantity', 1))  # Default to 1 if not provided

        # Check if the user already has this product in the cart
        cart_item, created = Cart.objects.get_or_create(
            customer=customer, product=product
        )

        if not created:
            # If the item already exists in the cart, update the quantity
            cart_item.quantity += quantity
        else:
            # If it's a new item, set the quantity
            cart_item.quantity = quantity
        cart_item.save()

        # Redirect to the product list page after adding the product
        return redirect('product-list')



class CartView(LoginRequiredMixin, View):
    def get(self, request):
        customer = request.user.customer  # Assuming each user has a related Customer instance
        cart_items = Cart.objects.select_related('product').filter(customer=customer)
        
        total_price = 0
        for item in cart_items:
            item.total = item.product.price * item.quantity  # Store the total price for each item
            total_price += item.total  # Add to the grand total

        return render(request, 'cart.html', {
            'cart_items': cart_items,
            'total_price': total_price
        })
        
class CheckoutView(LoginRequiredMixin, View):

    def get(self, request):
        customer = request.user.customer
        cart_items = Cart.objects.filter(customer=customer)
        
        total_price = 0
        for item in cart_items:
            item.total = item.product.price * item.quantity
            total_price += item.total
        
        return render(request, 'checkout.html', {
            'cart_items': cart_items,
            'total_price': total_price,
            'discount': 0,
            'final_price': total_price,
        })
    
    def post(self, request):
        customer = request.user.customer
        cart_items = Cart.objects.filter(customer=customer)
        
        total_price = 0
        for item in cart_items:
            item.total = item.product.price * item.quantity
            total_price += item.total
        
        coupon_code = request.POST.get('coupon_code')
        discount = 0
        final_price = total_price

        # Prepare the data for API request
        coupon_data = {
            'coupon_code': coupon_code,
            'total_price': total_price
        }

        # Send the request to the coupons API
        try:
            response = requests.post('http://127.0.0.1:8000/api/coupons/apply/', data=coupon_data)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    discount = result.get('discount_value', 0)
                    final_price = total_price - Decimal(discount)
                else:
                    # If coupon is invalid or expired
                    error_message = result.get('message', 'Invalid coupon')
                    # You can display the error message on the frontend
                    print(error_message)
            else:
                print("Error with coupon API", response.status_code)

        except requests.exceptions.RequestException as e:
            print(f"Error while requesting coupon API: {e}")

        return render(request, 'checkout.html', {
            'cart_items': cart_items,
            'total_price': total_price,
            'discount': discount,
            'final_price': final_price
        })

    
