from django.db import models
from django.contrib.auth.models import User
from ecommerce.models import Product




class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)  
    phone_number = models.CharField(max_length=15)
    email = models.CharField(max_length=100)
    referral_code = models.CharField(max_length=20, null=True, blank=True)  # Optional referral code

    def __str__(self):
        return self.name

class Cart(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='cart')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(null=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"
