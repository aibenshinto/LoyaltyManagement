from django.shortcuts import render

def coupon_page(request):
    return render(request, 'create_coupon.html')