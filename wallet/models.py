<<<<<<< HEAD
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
    
=======
from django.db import models


# Create your models here.
from coupons.models import Vendor
class CustomerVendor(models.Model):
    customerid = models.CharField(max_length=255) 
    vendorkey = models.ForeignKey(Vendor, on_delete=models.CASCADE) 
    def __str__(self):
        return self.customerid

class Wallet(models.Model):
    customer_vendor = models.ForeignKey(CustomerVendor, on_delete=models.CASCADE) 
    coins = models.IntegerField()

    def __str__(self):
        return self.customer_vendor
>>>>>>> 50b8c76e58e92ff6883a001f74cad939c4d001e7
