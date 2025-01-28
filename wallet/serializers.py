from rest_framework import serializers
from .models import CustomerVendor, Wallet
from authentication.models import Vendor

from rest_framework import serializers

# class CustomerDataSerializer(serializers.Serializer):
    
#     model = CustomerVendor
#     fields = '__all__'

class CustomerDataSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    business_name = serializers.CharField(max_length=255)
    referral_code = serializers.CharField(max_length=6, required=False)

    def validate_business_name(self, value):
        """
        Validate that the provided business_name exists in the Vendor model.
        """
        if not Vendor.objects.filter(business_name=value).exists():
            raise serializers.ValidationError("Business name is invalid.")
        return value