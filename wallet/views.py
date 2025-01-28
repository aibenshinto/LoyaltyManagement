from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomerVendor, Wallet
from authentication.models import Vendor
from .serializers import CustomerDataSerializer
import random
import string

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
                "business_name": vendor.business_name,  # Change from vendor_key to business_name
                "coins": Wallet.objects.get(customer_vendor=customer_vendor).coins,
                "referral_code": customer_vendor.referral_code  # Include referral_code here
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

                # Create wallet for new customer
                wallet = Wallet.objects.create(customer_vendor=customer_vendor, coins=20)
                message = f"Welcome! You have been awarded 20 coins as a signup bonus. Your referral code is {referral_code_generated}."
            else:
                wallet, wallet_created = Wallet.objects.get_or_create(customer_vendor=customer_vendor)
                message = f"Welcome back! You currently have {wallet.coins} coins."

            # Handle referral code if provided
            if referral_code:
                try:
                    referrer = CustomerVendor.objects.get(referral_code=referral_code)
                    referrer_wallet, _ = Wallet.objects.get_or_create(customer_vendor=referrer)

                    # Award coins to both referrer and new customer
                    wallet.coins += 10  # Add 10 coins to the new customer for using the referral code
                    wallet.save()

                    referrer_wallet.coins += 5  # Add 5 coins to the referrer for referring
                    referrer_wallet.save()

                    message += f" You have used a referral code. Both you and the referrer have received coins."

                except CustomerVendor.DoesNotExist:
                    return Response({"error": "Referral code is invalid."}, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "message": message,
                "customer_id": customer_id,
                "business_name": business_name,
                "coins": wallet.coins
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
