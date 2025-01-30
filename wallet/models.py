# from django.db import models

# from authentication.models import Vendor

# # Create your models here.

# class CustomerVendor(models.Model):
#     customerid = models.CharField(max_length=255) 
#     vendorkey = models.ForeignKey(Vendor , on_delete=models.CASCADE) 
#     referral_code = models.CharField(max_length=6, unique=True, null=True, blank=True)  # Add this field
#     def __str__(self):
#         return self.customerid 

# class Wallet(models.Model):
#     customer_vendor = models.ForeignKey(CustomerVendor, on_delete=models.CASCADE) 
#     coins = models.IntegerField()

#     def __str__(self):
#         return self.customer_vendor
    
from django.db import models

from authentication.models import Vendor

# Create your models here.

class CustomerVendor(models.Model):
    customerid = models.CharField(max_length=255) 
    vendorkey = models.ForeignKey(Vendor , on_delete=models.CASCADE) 
    referral_code = models.CharField(max_length=6, unique=True, null=True, blank=True)  # Add this field
    def _str_(self):
        return self.customerid 

class Wallet(models.Model):
    customer_vendor = models.ForeignKey(CustomerVendor, on_delete=models.CASCADE) 
    coins = models.IntegerField()

    def _str_(self):
        return self.customer_vendor
 
# Model to store Signup Bonus configuration (now with Vendor foreign key)
class LoyaltyConfiguration(models.Model):
    vendorkey = models.ForeignKey(Vendor , on_delete=models.CASCADE)
    signup_bonus_coins = models.IntegerField(default=0)
    referee_bonus_coins = models.IntegerField(default=0)
    referrer_bonus_coins = models.IntegerField(default=0)
    coin_value = models.IntegerField() 
    currency = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class PurchaseRule(models.Model):
    loyalty_config = models.ForeignKey(LoyaltyConfiguration, on_delete=models.CASCADE, related_name='purchase_rules')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    coins = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['amount']