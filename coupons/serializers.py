from rest_framework import serializers
from .models import Vendor, Coupon, DiscountCoupon, BOGOCoupon
from django.contrib.auth.models import User


class VendorRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField()

    class Meta:
        model = Vendor
        fields = ['business_name', 'address', 'username', 'password', 'email']

    def create(self, validated_data):
        user_data = {
            'username': validated_data.pop('username'),
            'email': validated_data.pop('email'),
            'password': validated_data.pop('password')
        }
        user = User.objects.create_user(**user_data)
        vendor = Vendor.objects.create(user=user, **validated_data)
        return vendor


class CouponSerializer(serializers.ModelSerializer):
    # Set vendor as read-only without providing the queryset
    vendor = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Coupon
        fields = '__all__'

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

class BOGOCouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = BOGOCoupon
        fields = ['product_to_buy', 'free_product']
        
   
class ApplyCouponSerializer(serializers.Serializer):
    coupon_code = serializers.CharField(max_length=20)
    total_price = serializers.DecimalField(max_digits=10,decimal_places=2)
    vendor_key = serializers.UUIDField()