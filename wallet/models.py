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