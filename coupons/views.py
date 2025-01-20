from django.shortcuts import render, redirect
from .forms import CouponForm
from .models import Coupon

def create_coupon(request):
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            coupon = form.save(commit=False)
            coupon.created_by = request.user.created_by
            coupon.save()
            return redirect('coupon_success')  # Redirect to a success page
    else:
        form = CouponForm()
    
    return render(request, 'create_coupon.html', {'form': form})

def coupon_success(request):
    return render(request, 'coupon_success.html')