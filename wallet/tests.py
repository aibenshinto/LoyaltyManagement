from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomerVendor, Wallet
from authentication.models import Vendor
from .serializers import CustomerDataSerializer

class RequestCustomerDataView(APIView):
    def post(self, request):
        serializer = CustomerDataSerializer(data=request.data)
        if serializer.is_valid():
            # Extract validated data
            customer_id = serializer.validated_data['customer_id']
            vendor_key = serializer.validated_data['vendor_key']
            referral_code = serializer.validated_data.get('referral_code', None)

            # Get the vendor instance
            try:
                vendor = Vendor.objects.get(vendorkey=vendor_key)
            except Vendor.DoesNotExist:
                return Response({"error": "Vendor key is invalid."}, status=status.HTTP_400_BAD_REQUEST)

            # Check if the customer already exists for this vendor
            customer_vendor, created = CustomerVendor.objects.get_or_create(
                customerid=customer_id,
                vendorkey=vendor
            )

            if created:
                # If the customer is new, create a wallet with 20 coins
                Wallet.objects.create(customer_vendor=customer_vendor, coins=20)
                message = "Welcome! You have been awarded 20 coins as a signup bonus."
            else:
                # If the customer already exists, just fetch their wallet info
                wallet = Wallet.objects.get(customer_vendor=customer_vendor)
                message = f"Welcome back! You currently have {wallet.coins} coins."

            # Handle referral code logic (if applicable)
            if referral_code:
                # Example: award referral bonus or log referral
                message += " Referral bonus will be processed if applicable."

            # Return success response
            return Response({
                "message": message,
                "customer_id": customer_id,
                "vendor_key": vendor_key,
                "coins": Wallet.objects.get(customer_vendor=customer_vendor).coins
            }, status=status.HTTP_200_OK)

        # Return error response if validation fails
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        vendor_key = request.query_params.get('vendor_key', None)

        # Filter by vendor if vendor_key is provided
        if vendor_key:
            try:
                vendor = Vendor.objects.get(vendorkey=vendor_key)
            except Vendor.DoesNotExist:
                return Response({"error": "Vendor key is invalid."}, status=status.HTTP_400_BAD_REQUEST)
            customer_vendors = CustomerVendor.objects.filter(vendorkey=vendor)
        else:
            # Retrieve all customers if no vendor_key is specified
            customer_vendors = CustomerVendor.objects.all()

        # Prepare data to return
        data = [
            {
                "customer_id": customer.customerid,
                "vendor_key": customer.vendorkey.vendorkey,
                "vendor_name": customer.vendorkey.name,  # Assuming Vendor has a name field
                "coins": Wallet.objects.get(customer_vendor=customer).coins,
                "signup_bonus": 20,  # Assuming 20 coins is the signup bonus
                "referral_code_used": customer.referral_code is not None,  # Check if a referral code was used
            }
            for customer in customer_vendors
        ]

        return Response({"customers": data}, status=status.HTTP_200_OK)
