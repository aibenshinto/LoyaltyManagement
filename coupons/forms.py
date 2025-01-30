from django import forms
from .models import Coupon,DiscountCoupon
from .models import Vendor
from django.contrib.auth.models import User

class CouponForm(forms.ModelForm):
    class Meta:
        model = Coupon
        fields = [ 'code', 'min_purchase_amount', 'valid_from', 'valid_until']

    def clean(self):
        cleaned_data = super().clean()
        widgets = {
            'valid_from': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'valid_until': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class DiscountCouponForm(forms.ModelForm):
    class Meta:
        model = DiscountCoupon
        fields = ['discount_amount', 'discount_percentage']
    
class ApplyCouponForm(forms.Form):
    coupon_code = forms.CharField(max_length=20, label='Enter Coupon Code')