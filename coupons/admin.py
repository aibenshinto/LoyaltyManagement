from django.contrib import admin
from .models import Coupon, DiscountCoupon

# Register Coupon model to manage coupons
class CouponAdmin(admin.ModelAdmin):
    list_display = ('vendor', 'code', 'valid_from', 'valid_until')
    search_fields = ('code', 'vendor__username')  # Add search functionality by coupon code and vendor username
    list_filter = ('vendor', 'valid_from', 'valid_until')  # Add filters for easy searching

admin.site.register(Coupon, CouponAdmin)

# Register DiscountCoupon and BOGOCoupon models
class DiscountCouponAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'discount_amount', 'discount_percentage')

admin.site.register(DiscountCoupon, DiscountCouponAdmin)

class BOGOCouponAdmin(admin.ModelAdmin):
    list_display = ('coupon', 'product_to_buy', 'free_product')


