from rest_framework import serializers
from .models import CustomerVendor, Wallet
from authentication.models import Vendor

class CustomerDataSerializer(serializers.Serializer):
    customer_id = serializers.CharField(max_length=255)
    vendor_key = serializers.CharField(max_length=255)
    referral_code = serializers.CharField(max_length=255, required=False)