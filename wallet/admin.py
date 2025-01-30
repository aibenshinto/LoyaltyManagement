from django.contrib import admin
from .models import CustomerVendor, LoyaltyConfiguration, PurchaseRule

# Register your models here.
admin.site.register(CustomerVendor)
admin.site.register(PurchaseRule)
admin.site.register(LoyaltyConfiguration)