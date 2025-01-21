from django.shortcuts import render, redirect
from .forms import CouponForm
from django.utils import timezone
from .models import Coupon
from .forms import ApplyCouponForm,CouponForm, DiscountCouponForm, BOGOCouponForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# @login_required
def create_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        discount_form = DiscountCouponForm(request.POST)
        bogo_form = BOGOCouponForm(request.POST)
        
        coupon_type = request.POST.get('coupon_type', '')  # Get the coupon type from the form

        if form.is_valid():
            # Save the main coupon data
            coupon = form.save(commit=False)
            coupon.vendor = request.user  # Assign the vendor creating the coupon
            coupon.save()

            # Check which coupon type is selected and save the corresponding rules
            if coupon_type == 'discount' and discount_form.is_valid():
                discount_rule = discount_form.save(commit=False)
                discount_rule.coupon = coupon
                discount_rule.save()

            elif coupon_type == 'bogo' and bogo_form.is_valid():
                bogo_rule = bogo_form.save(commit=False)
                bogo_rule.coupon = coupon
                bogo_rule.save()

            return redirect('coupon_success')  # Redirect after successful creation
    else:
        form = CouponForm()
        discount_form = DiscountCouponForm()
        bogo_form = BOGOCouponForm()

    return render(request, 'create_coupon.html', {
        'form': form,
        'discount_form': discount_form,
        'bogo_form': bogo_form
    })


def apply_coupon_logic(coupon_code, total_purchase_amount):
    try:
        coupon = Coupon.objects.get(code=coupon_code)
        if coupon.valid_from <= timezone.now() <= coupon.valid_until:
            # Check for the type of coupon and apply corresponding rules
            if hasattr(coupon, 'discount_rule'):
                discount_rule = coupon.discount_rule  # Related rule for discount coupon
                discount_value = discount_rule.get_discount_value(total_purchase_amount)
                final_amount = total_purchase_amount - discount_value
                return {"valid": True, "final_amount": final_amount, "discount_value": discount_value}

            # elif hasattr(coupon, 'bogo_rule'):
            #     bogo_rule = coupon.bogo_rule
            #     free_product = bogo_rule.apply_bogo(purchased_products)  # Check purchased products
            #     if free_product:
            #         return {"valid": True, "free_product": free_product}
            #     else:
            #         return {"valid": False, "message": "BOGO conditions not met."}

        else:
            return {"valid": False, "message": "Coupon is expired or not yet valid."}
    except Coupon.DoesNotExist:
        return {"valid": False, "message": "Invalid coupon code."}
    
    
def coupon_success(request):
    return render(request, 'coupon_success.html')


def apply_coupon(request):
    if request.method == 'POST':
        form = ApplyCouponForm(request.POST)
        if form.is_valid():
            coupon_code = form.cleaned_data['coupon_code']
            total_purchase_amount = 1000  # Assume this is fetched from the cart total

            # Try to apply the coupon
            result = apply_coupon_logic(coupon_code, total_purchase_amount)

            if result['valid']:
                messages.success(request, f"Coupon applied! You saved {result['discount_value']}!")
                return render(request, 'checkout.html', {'form': form, 'final_amount': result['final_amount']})
            else:
                messages.error(request, result['message'])
    else:
        form = ApplyCouponForm()

    return render(request, 'apply_coupon.html', {'form': form})