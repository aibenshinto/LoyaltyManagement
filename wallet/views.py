from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomerVendor, Wallet
from authentication.models import Vendor
from .serializers import CustomerDataSerializer

class RequestCustomerDataView(APIView):
    def get(self, request):
        # Retrieve all customers and vendors
        customer_vendors = CustomerVendor.objects.all()
        customers = []
        
        # Prepare data for each customer
        for customer_vendor in customer_vendors:
            vendor = customer_vendor.vendorkey  # Get the vendor object
            customer_data = {
                "customer_id": customer_vendor.customerid,
                "vendor_key": vendor.vendor_key,
                "coins": Wallet.objects.get(customer_vendor=customer_vendor).coins
            }
            customers.append(customer_data)

        return Response({"customers": customers}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CustomerDataSerializer(data=request.data)
        if serializer.is_valid():
            customer_id = serializer.validated_data['customer_id']
            vendor_key = serializer.validated_data['vendor_key']
            referral_code = serializer.validated_data.get('referral_code', None)

            # Validate Vendor
            try:
                vendor = Vendor.objects.get(vendor_key=vendor_key)
            except Vendor.DoesNotExist:
                return Response({"error": "Vendor key is invalid."}, status=status.HTTP_400_BAD_REQUEST)

            # Create or retrieve CustomerVendor
            customer_vendor, created = CustomerVendor.objects.get_or_create(
                customerid=customer_id,
                vendorkey=vendor
            )

            # Create wallet if the customer is newly created
            if created:
                Wallet.objects.create(customer_vendor=customer_vendor, coins=20)
                message = "Welcome! You have been awarded 20 coins as a signup bonus."
            else:
                wallet = Wallet.objects.get(customer_vendor=customer_vendor)
                message = f"Welcome back! You currently have {wallet.coins} coins."

            # Handle referral code if provided
            if referral_code:
                message += " Referral bonus will be processed if applicable."

            return Response({
                "message": message,
                "customer_id": customer_id,
                "vendor_key": vendor_key,
                "coins": Wallet.objects.get(customer_vendor=customer_vendor).coins
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
