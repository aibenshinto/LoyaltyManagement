from django.db import models
from django.contrib.auth.models import User

# Base Coupon Model
class Coupon(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE)  # Assuming each vendor is a user
    code = models.CharField(max_length=20, unique=True)  # Unique coupon code
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()

    def __str__(self):
        return f"Coupon for {self.vendor.username} - Code: {self.code}"

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

# BOGO Coupon Model with Specific Rules
class BOGOCoupon(models.Model):
    coupon = models.OneToOneField(Coupon, on_delete=models.CASCADE, related_name="bogo_rule")
    product_to_buy = models.CharField(max_length=100)  # Product to buy for the BOGO
    free_product = models.CharField(max_length=100)  # Free product to be given

    def apply_bogo(self, purchased_products):
        if self.product_to_buy in purchased_products:
            return self.free_product
        return None