from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'image')  # Display image field in admin
    list_editable = ('price', 'stock')  # Allow inline editing
