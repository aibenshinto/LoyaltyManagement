from rest_framework import serializers
from .models import CustomerVendor, Wallet
from authentication.models import Vendor

from rest_framework import serializers

from rest_framework import serializers

class CustomerDataSerializer(serializers.Serializer):
    customer_id = serializers.CharField(required=True)
    business_name = serializers.CharField(required=True)
    referral_code = serializers.CharField(required=False, allow_null=True, allow_blank=True)


    def validate_business_name(self, value):
        """
        Validate that the provided business_name exists in the Vendor model.
        """
        if not Vendor.objects.filter(business_name=value).exists():
            raise serializers.ValidationError("Business name is invalid.")
        return value

