from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomerVendor, Wallet
from authentication.models import Vendor
from .serializers import CustomerDataSerializer, PurchaseRewardSerializer,CustomerRedeemSerializer
import random
import string
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.http import HttpResponse


from django.contrib import messages
from django.http import HttpResponse
# View to display and handle the form for configuring loyalty settings

from django.http import HttpResponse


from authentication.models import Vendor


from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import LoyaltyConfiguration, PurchaseRule
import json

@login_required

def loyalty_config(request):
    if request.method == 'POST':
        try:
            # Debugging: print POST data
            print("POST data:", request.POST)
            vendor = Vendor.objects.get(user=request.user)

            # Create or update LoyaltyConfiguration
            config = LoyaltyConfiguration.objects.create(
                vendorkey=vendor,
                signup_bonus_coins=int(request.POST.get('signupBonusCoins', 0)),
                referee_bonus_coins=int(request.POST.get('refereeBonusCoins', 0)),
                referrer_bonus_coins=int(request.POST.get('referrerBonusCoins', 0)),
                coin_value=int(request.POST.get('coinValue', 0)),
                currency=request.POST.get('currency', '')
            )
            config.save()
            print(f"Saved LoyaltyConfiguration: {config.id}")

            # Debugging: Check if LoyaltyConfiguration is created
            print(f"Created LoyaltyConfiguration: {config}")

            # Handle purchase rules
            purchase_rules_data = []
            i = 0
            while True:
                amount = request.POST.get(f'purchaseRules[{i}][amount]')
                coins = request.POST.get(f'purchaseRules[{i}][coins]')
                
                if amount is None or coins is None:
                    break
                
                # Create purchase rule
                rule = PurchaseRule.objects.create(
                    loyalty_config=config,
                    amount=float(amount),
                    coins=int(coins)
                )
                
                # Debugging: Check if PurchaseRule is created
                print(f"Created PurchaseRule: {rule}")
                i += 1

            messages.success(request, 'Loyalty configuration saved successfully!')
            return redirect('loyalty_configuration')

        except Exception as e:
            # Debugging: print error message
            print(f"Error saving configuration: {str(e)}")
            messages.error(request, f'Error saving configuration: {str(e)}')
            return redirect('loyalty_configuration')

    # Get the latest configuration
    latest_config = LoyaltyConfiguration.objects.last()
    purchase_rules = []
    if latest_config:
        purchase_rules = latest_config.purchase_rules.all()

    return render(request, 'loyalty_config.html', {
        'config': latest_config,
        'purchase_rules': purchase_rules
    })
class RequestCustomerDataView(APIView):
    def generate_referral_code(self):
        """Generate a random 6-character referral code."""
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

    def get(self, request):
        # Retrieve all customers and vendors
        customer_vendors = CustomerVendor.objects.all()
        customers = []

        for customer_vendor in customer_vendors:
            vendor = customer_vendor.vendorkey  # Get the vendor object
            customer_data = {
                "customer_id": customer_vendor.customerid,
                "business_name": vendor.business_name,  
                "coins": Wallet.objects.get(customer_vendor=customer_vendor).coins,
                "referral_code": customer_vendor.referral_code  
            }
            customers.append(customer_data)

        return Response({"customers": customers}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CustomerDataSerializer(data=request.data)
        if serializer.is_valid():
            customer_id = serializer.validated_data['customer_id']
            business_name = serializer.validated_data['business_name']
            referral_code = serializer.validated_data.get('referral_code', None)

            # Validate Vendor
            try:
                vendor = Vendor.objects.get(business_name=request.data['business_name'])
            except Vendor.DoesNotExist:
                return Response({"error": "Business name is invalid."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the most recent LoyaltyConfiguration for this vendor
            try:
                loyalty_config = LoyaltyConfiguration.objects.filter(vendorkey=vendor).latest('created_at')
            except LoyaltyConfiguration.DoesNotExist:
                return Response({"error": "Loyalty configuration not found for this vendor."}, status=status.HTTP_400_BAD_REQUEST)

            signup_bonus = loyalty_config.signup_bonus_coins
            referee_bonus = loyalty_config.referee_bonus_coins
            referrer_bonus = loyalty_config.referrer_bonus_coins

            # Create or retrieve CustomerVendor
            customer_vendor, created = CustomerVendor.objects.get_or_create(
                customerid=customer_id,
                vendorkey=vendor
            )

            # If new customer, generate a referral code
            if created:
                referral_code_generated = self.generate_referral_code()
                customer_vendor.referral_code = referral_code_generated
                customer_vendor.save()

                # Create wallet for new customer with signup bonus coins
                wallet = Wallet.objects.create(customer_vendor=customer_vendor, coins=signup_bonus)
                message = f"Welcome! You have been awarded {signup_bonus} coins as a signup bonus. Your referral code is {referral_code_generated}."
            else:
                wallet, wallet_created = Wallet.objects.get_or_create(customer_vendor=customer_vendor)
                message = f"Welcome back! You currently have {wallet.coins} coins."

            # Handle referral code if provided
            if referral_code:
                try:
                    referrer = CustomerVendor.objects.get(referral_code=referral_code)
                    referrer_wallet, _ = Wallet.objects.get_or_create(customer_vendor=referrer)

                    # Award coins using the values from LoyaltyConfiguration
                    wallet.coins += referee_bonus  # Add coins to the new customer
                    wallet.save()

                    referrer_wallet.coins += referrer_bonus  # Add coins to the referrer
                    referrer_wallet.save()

                    message += f" You have used a referral code. You received {referee_bonus} coins, and the referrer received {referrer_bonus} coins."

                except CustomerVendor.DoesNotExist:
                    return Response({"error": "Referral code is invalid."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "message": message,
                "customer_id": customer_id,
                "business_name": business_name,
                "coins": wallet.coins
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PurchaseRewardsView(APIView):
    def post(self, request):
        serializer = PurchaseRewardSerializer(data=request.data)
        if serializer.is_valid():
            customer_id = serializer.validated_data['customer_id']
            business_name = serializer.validated_data['business_name']
            total_price = serializer.validated_data['total_price']

            # Validate Vendor
            try:
                vendor = Vendor.objects.get(business_name=business_name)
            except Vendor.DoesNotExist:
                return Response({"error": "Business name is invalid."}, status=status.HTTP_400_BAD_REQUEST)

            # Get customer-vendor relationship
            try:
                customer_vendor = CustomerVendor.objects.get(
                    customerid=customer_id,
                    vendorkey=vendor
                )
            except CustomerVendor.DoesNotExist:
                return Response({"error": "Customer not found for this vendor."}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch the most recent LoyaltyConfiguration
            try:
                loyalty_config = LoyaltyConfiguration.objects.filter(
                    vendorkey=vendor
                ).latest('created_at')
            except LoyaltyConfiguration.DoesNotExist:
                return Response({"error": "Loyalty configuration not found for this vendor."}, status=status.HTTP_400_BAD_REQUEST)

            # Get ALL applicable purchase rules for this purchase amount
            applicable_rules = PurchaseRule.objects.filter(
                loyalty_config=loyalty_config,  # Only rules from latest config
                amount__lte=total_price        # All rules less than or equal to purchase amount
            ).order_by('-amount')              # Sort by amount descending

            if not applicable_rules.exists():
                return Response({
                    "message": "No applicable purchase rules found for this amount.",
                    "customer_id": customer_id,
                    "business_name": business_name,
                    "purchase_amount": total_price,
                    "available_rules": list(PurchaseRule.objects.filter(
                        loyalty_config=loyalty_config
                    ).values('amount', 'coins')),
                    "coins": Wallet.objects.get(customer_vendor=customer_vendor).coins
                }, status=status.HTTP_200_OK)

            # Get the best rule (highest amount that's less than purchase)
            best_rule = applicable_rules.first()
            reward_coins = best_rule.coins

            # For debugging/transparency, let's include all rules that were checked
            all_checked_rules = [{
                'amount': rule.amount,
                'coins': rule.coins,
                'was_applied': (rule.id == best_rule.id)
            } for rule in applicable_rules]

            # Update wallet
            wallet = Wallet.objects.get(customer_vendor=customer_vendor)
            previous_coins = wallet.coins
            wallet.coins += reward_coins
            wallet.save()

            return Response({
                "message": f"Purchase reward applied successfully! You earned {reward_coins} coins for your purchase of {total_price}.",
                "customer_id": customer_id,
                "business_name": business_name,
                "purchase_amount": total_price,
                "coins": wallet.coins,
                "coins_earned": reward_coins,
                "previous_balance": previous_coins,
                "rule_applied": {
                    "amount": best_rule.amount,
                    "coins": best_rule.coins
                },
                "all_checked_rules": all_checked_rules  # Shows all rules that were considered
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RequestCustomerRedeemView(APIView):
   def post(self, request):
       serializer = CustomerRedeemSerializer(data=request.data)
       if serializer.is_valid():
           customer_id = serializer.validated_data['customer_id']
           business_name = serializer.validated_data['business_name']
           referral_code = serializer.validated_data.get('referral_code', None)
           total_price = serializer.validated_data['total_price']
           no_of_coins = serializer.validated_data['no_of_coins']
           currency = serializer.validated_data['currency']


           # Validate Vendor
           try:
               vendor = Vendor.objects.get(business_name=business_name)
           except Vendor.DoesNotExist:
               return Response({"error": "Business name is invalid."}, status=status.HTTP_400_BAD_REQUEST)


           # Retrieve or create CustomerVendor and Wallet
           customer_vendor, created = CustomerVendor.objects.get_or_create(
               customerid=customer_id,
               vendorkey=vendor
           )
           wallet, _ = Wallet.objects.get_or_create(customer_vendor=customer_vendor)


           # Check if the wallet has enough coins
           if wallet.coins < no_of_coins:
               return Response({"error": "Not enough coins in the wallet."}, status=status.HTTP_400_BAD_REQUEST)


           # Retrieve coin value and weight from LoyaltyConfiguration for the vendor
           try:
               loyalty_config = LoyaltyConfiguration.objects.get(vendorkey=vendor, currency=currency)
               coin_value = loyalty_config.coin_value
           except LoyaltyConfiguration.DoesNotExist:
               return Response({"error": "No loyalty configuration found for the vendor in the given currency."}, status=status.HTTP_400_BAD_REQUEST)


           # Calculate total coin weight and reduced price
           total_coin_weight = no_of_coins * coin_value
           reduced_price = total_price - total_coin_weight


           # Update the wallet by reducing the number of coins
           wallet.coins -= no_of_coins
           wallet.save()


           return Response({
               "message": "Transaction successful.",
               "customer_id": customer_id,
               "business_name": business_name,
               "original_price": total_price,
               "reduced_price": reduced_price,
               "coins_used": no_of_coins,
               "remaining_coins": wallet.coins,
               "currency": currency
           }, status=status.HTTP_200_OK)


       return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
