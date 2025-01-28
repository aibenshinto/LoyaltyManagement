from django.db import models
from django.contrib.auth.models import User
from authentication.models import Vendor


# class Vendor(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='vendor')
#     business_name = models.CharField(max_length=255)
#     phone_number = models.CharField(max_length=15, unique=True)
#     email = models.EmailField(unique=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     is_active = models.BooleanField(default=True)
#     vendor_key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)  # Auto-generated unique ID

# Base Coupon Model
class Coupon(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)  
    code = models.CharField(max_length=20, unique=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()

    def __str__(self):
        return f"Coupon for {self.vendor.user} - Code: {self.code}"

# Discount Coupon Model with Specific Rules
class DiscountCoupon(models.Model):
    coupon = models.OneToOneField(Coupon, on_delete=models.CASCADE, related_name="discount_rule")
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    def get_discount_value(self, total_purchase_amount):
        if self.discount_amount:
            return self.discount_amount
        elif self.discount_percentage:
            return (self.discount_percentage / 100) * total_purchase_amount
        return 0

# Min Purchase Coupon Model with Specific Rules
class MinPurchaseCoupon(models.Model):
    coupon = models.OneToOneField(Coupon, on_delete=models.CASCADE, related_name="min_purchase_rule")
    minimum_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # for discount reward
    coin_reward = models.IntegerField(null=True, blank=True)  # for coin reward
    
    def apply_reward(self, total_purchase_amount):
        if total_purchase_amount >= self.minimum_purchase_amount:
            if self.discount_amount:
                return {'reward': 'discount', 'discount_value': self.discount_amount}
            elif self.coin_reward: 
                return {'reward': 'coins', 'coins_awarded': self.coin_reward}
        else:
            return {'reward': 'none'}
