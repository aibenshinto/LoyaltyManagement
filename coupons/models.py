from django.db import models
from django.contrib.auth.models import User
from authentication.models import Vendor


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
    reward_type_choices = [
        ('discount', 'Discount Coupon'),
        ('coins', 'Coins Reward')
    ]
    reward_type = models.CharField(max_length=10, choices=reward_type_choices)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # for discount reward
    coin_reward = models.IntegerField(null=True, blank=True)  # for coin reward
