from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .models import Customer, Product, Cart
import requests
from decimal import Decimal
from django.db import transaction
import json
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages


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
        business_name = "vendor2" # change business name accordingly

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
            messages.success(request, "Registration successful! You can now log in.")
            
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


class ProductListView(LoginRequiredMixin,View):
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
        error_message = None
        customer = request.user.customer
        cart_items = Cart.objects.filter(customer=customer)

        # Calculate initial total price
        total_price = 0
        for item in cart_items:
            item.total = item.product.price * item.quantity
            total_price += item.total

        # Initialize variables
        coupon_code = request.POST.get('coupon_code')
        discount = 0
        price_after_coupon = total_price
        business_name = request.POST.get('business_name', "vendor2")  # change business name accordingly

        # Apply coupon if provided
        if coupon_code:
            coupon_data = {
                'coupon_code': coupon_code,
                'total_price': float(total_price),
                'business_name': business_name,
                'cust_id': str(customer.id)
            }

            try:
                response = requests.post(
                    'http://127.0.0.1:8000/coupons/api/coupons/apply/',
                    json=coupon_data
                )
                if response.status_code == 200:
                    result = response.json()
                    if result.get('success'):
                        discount = Decimal(result.get('discount_value', 0))
                        price_after_coupon = total_price - discount
                    else:
                        error_message = result.get('message', 'Invalid coupon')
                else:
                    error_message = "Error with coupon API"
            except requests.exceptions.RequestException as e:
                error_message = f"Error while requesting coupon API: {e}"

        # Initialize final price after coupon
        final_price = price_after_coupon

        # Handle wallet balance redemption
        no_of_coins = int(request.POST.get('wallet_balance', 0))  # Wallet input from form
        currency = request.POST.get('currency', 'INR')  # Default currency

        if no_of_coins > 0:
            redeem_data = {
                'customer_id': customer.id,
                'business_name': business_name,
                'total_price': float(price_after_coupon),  # Apply after coupon discount
                'no_of_coins': no_of_coins,
                'currency': currency
            }

            try:
                response = requests.post(
                    'http://127.0.0.1:8000/api/redeem-coin/',
                    json=redeem_data
                )
                if response.status_code == 200:
                    result = response.json()
                    final_price = result.get('reduced_price', price_after_coupon)
                else:
                    error_message = response.json().get('error', 'Wallet redemption failed')
            except requests.exceptions.RequestException as e:
                error_message = f"Error connecting to wallet API: {e}"

        return render(request, 'checkout.html', {
            'cart_items': cart_items,
            'total_price': total_price,
            'discount': discount,
            'final_price': final_price,
            'error_message': error_message
        })



class WalletView(LoginRequiredMixin, View):
    def get(self, request):
        # Assuming the user is authenticated
        customer = request.user.customer  # Retrieve the Customer instance linked to the User

        try:
            # Make a GET request to the API to retrieve all customers' wallet data
            response = requests.get('http://127.0.0.1:8000/api/customer-data/')

            if response.status_code == 200:
                wallet_data = response.json()  # Parse the JSON response
                # print(f"Wallet data retrieved: {wallet_data}")  # Debugging: Print full wallet data

                # Find the wallet data for the signed-in customer
                customer_wallet = next(
                    (item for item in wallet_data['customers'] if int(item['customer_id']) == customer.id),
                    None
                )
                print(f"Customer wallet data: {customer_wallet}")  # Debugging: Print matched customer wallet data

                if customer_wallet:
                    balance = customer_wallet.get('coins', 0)  # Retrieve the coin balance
                    referral_code = customer_wallet.get('referral_code', 'N/A')  # Retrieve referral code
                    print(f"Customer referral code: {referral_code}")  # Debugging: Print referral code
                else:
                    balance = "Error: Wallet data for the customer not found"
                    referral_code = "Error: Referral code not found"
            else:
                balance = "Error retrieving wallet data from the API"
                referral_code = "Error retrieving referral code"
                print(f"API response error: {response.status_code}")  # Debugging: Print API error status code

        except requests.exceptions.RequestException as e:
            balance = f"Error connecting to wallet API: {e}"
            referral_code = "Error connecting to wallet API"
            print(balance)  # Debugging: Log connection error

        # Render the wallet page with the balance and referral code
        return render(request, 'wallet.html', {'balance': balance, 'referral_code': referral_code})


class PaymentView(LoginRequiredMixin, View):
    def post(self, request):
        customer = request.user.customer
        cart_items = Cart.objects.filter(customer=customer)
        
        total_price = 0
        for item in cart_items:
            item.total = item.product.price * item.quantity
            total_price += item.total

        # Simulate dummy payment
        payment_status = "success"  # Simulate a successful payment

        if payment_status == "success":
            # After successful payment, prepare data for the API request
            business_name = "vendor2"
            payload = {
                'customer_id': customer.id,
                'business_name': business_name,
                'total_price': float(total_price)
            }

            # Call the external API (RequestCustomerDataView)
            try:
                response = requests.post(
                    'http://127.0.0.1:8000/api/purchase-data/',
                    json=payload
                )
                if response.status_code == 200:
                    # Clear the cart after successful payment and API request
                    cart_items.delete()
                    return JsonResponse({'message': 'Payment successful and data sent!'}, status=200)
                else:
                    print(f"API error: {response.status_code}")
                    return JsonResponse({'error': 'Payment successful but data submission failed.'}, status=500)
            except requests.RequestException as e:
                print(f"API call failed: {e}")
                return JsonResponse({'error': 'Payment successful but data submission failed.'}, status=500)

        return JsonResponse({'error': 'Payment failed.'}, status=400)