from django.shortcuts import render

def coupon_page(request):
    return render(request, 'vendor_register.html')