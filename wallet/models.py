from django.db import models

from authentication.models import Vendor

# Create your models here.

class CustomerVendor(models.Model):
    customerid = models.CharField(max_length=255) 
    vendorkey = models.ForeignKey(Vendor , on_delete=models.CASCADE) 
    referral_code = models.CharField(max_length=6, unique=True, null=True, blank=True)  # Add this field
    def __str__(self):
        return self.customerid 

class Wallet(models.Model):
    customer_vendor = models.ForeignKey(CustomerVendor, on_delete=models.CASCADE) 
    coins = models.IntegerField()

    def __str__(self):
        return self.customer_vendor