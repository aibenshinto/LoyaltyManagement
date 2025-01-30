from rest_framework import serializers
from .models import Vendor, Coupon, DiscountCoupon, MinPurchaseCoupon
from django.contrib.auth.hashers import make_password

class  CouponSerializer(serializers.ModelSerializer):
    # Set vendor as read-only without providing the queryset
    vendor = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Coupon
        fields = "__all__"

    def create(self, validated_data):
        # Get the logged-in user from the request context
        user = self.context['request'].user
        try:
            # Fetch the vendor based on the logged-in user
            vendor = Vendor.objects.get(user=user)
        except Vendor.DoesNotExist:
            raise serializers.ValidationError("Vendor not found for the current user.")

        # Add the vendor to the validated data before saving
        validated_data['vendor'] = vendor
        coupon = Coupon.objects.create(**validated_data)
        return coupon
        

class DiscountCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscountCoupon
        fields = ['discount_amount', 'discount_percentage']

class MinPurchaseCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = MinPurchaseCoupon
        fields = ['minimum_purchase_amount', 'discount_amount', 'coin_reward']
        

class ApplyCouponSerializer(serializers.Serializer):
    coupon_code = serializers.CharField(max_length=20)
    total_price = serializers.DecimalField(max_digits=10,decimal_places=2)
    business_name = serializers.CharField(max_length=20)
    cust_id = serializers.CharField(max_length=20)