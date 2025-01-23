from django.db import models

from authentication.models import Vendor

# Create your models here.

class CustomerVendor(models.Model):
    customerid = models.CharField(max_length=255) 
    vendorkey = models.ForeignKey(Vendor , on_delete=models.CASCADE) 
    def __str__(self):
        return self.customerid