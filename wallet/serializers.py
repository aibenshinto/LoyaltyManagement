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

class PurchaseRewardSerializer(serializers.Serializer):
    customer_id = serializers.CharField()
    business_name = serializers.CharField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_total_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Total price must be greater than 0")
        return value
    

class CustomerRedeemSerializer(serializers.Serializer):
   customer_id = serializers.CharField(required=True)
   business_name = serializers.CharField(required=True)
   referral_code = serializers.CharField(required=False, allow_null=True, allow_blank=True)
   total_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)  # Total price
   no_of_coins = serializers.IntegerField(required=True)  # Number of coins
   currency = serializers.CharField(max_length=10, required=True)  # Currency


   def validate_business_name(self, value):
       """
       Validate that the provided business_name exists in the Vendor model.
       """
       if not Vendor.objects.filter(business_name=value).exists():
           raise serializers.ValidationError("Business name is invalid.")
       return value
   
   