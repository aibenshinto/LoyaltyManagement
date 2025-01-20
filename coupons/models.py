from django.db import models
from django.utils import timezone


class Vendor(models.Model):
    name = models.CharField(max_length=10)

class Coupon(models.Model):
    code = models.CharField(max_length=10)
    created_by = models.ForeignKey(Vendor,on_delete=models.CASCADE)
    is_claimed = models.BooleanField(default=False)
    expiry_date = models.DateTimeField()
    usage_limit = models.IntegerField(default=1)
    times_used = models.IntegerField(default=0)
    
    def __str__(self):
        return self.code
    
    def is_valid(self):
        return self.is_claimed and self.expiry_date > timezone.now() and self.times_used < self.usage_limit
    