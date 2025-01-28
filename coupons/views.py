from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Coupon,Vendor
from .serializers import ApplyCouponSerializer, CouponSerializer, DiscountCouponSerializer, MinPurchaseCouponSerializer
from rest_framework.views import APIView
from wallet.models import CustomerVendor
from django.shortcuts import render
from django.contrib.auth.decorators import login_required



@login_required(login_url='vendor_login')
def create_coupon_view(request):
    if request.method == 'GET':
        return render(request, 'create_coupon.html')

    elif request.method == 'POST':
        coupon_type = request.POST.get('coupon_type', '')

        try:
            vendor = Vendor.objects.get(user=request.user)
        except Vendor.DoesNotExist:
            return render(request, 'create_coupon.html', {"message": "Vendor not found for the current user."})

        coupon_serializer = CouponSerializer(data=request.POST, context={'request': request})
        if coupon_serializer.is_valid():
            coupon = coupon_serializer.save(vendor=vendor)

            if coupon_type == 'discount':
                discount_serializer = DiscountCouponSerializer(data=request.POST, context={'request': request})
                if discount_serializer.is_valid():
                    discount_coupon = discount_serializer.save(coupon=coupon)
                    return render(request, 'create_coupon.html', {"message": "Discount coupon created successfully"})
            
            elif coupon_type == 'min_purchase':
                min_purchase_serializer = MinPurchaseCouponSerializer(data=request.POST, context={'request': request})
                if min_purchase_serializer.is_valid():
                    min_purchase_coupon = min_purchase_serializer.save(coupon=coupon)
                    return render(request, 'create_coupon.html', {"message": "Min Purchase coupon created successfully"})
        
        # If form is invalid, return errors
        return render(request, 'create_coupon.html', {"errors": coupon_serializer.errors})


# Apply Coupon Logic
def apply_coupon_logic(coupon_code, total_purchase_amount, business_name, user):
    try:
        vendor = Vendor.objects.get(business_name=business_name)
        coupon = Coupon.objects.get(code=coupon_code,vendor = vendor)
        
        if not CustomerVendor.objects.filter(customerid=user, vendorkey=vendor).exists():
                return {"valid": False, "message": "You are not a customer of this vendor."}
        
        if coupon.valid_from <= timezone.now() <= coupon.valid_until:
            # Check for the type of coupon and apply corresponding rules
            if hasattr(coupon, 'discount_rule'):
                discount_rule = coupon.discount_rule  # Related rule for discount coupon
                discount_value = discount_rule.get_discount_value(total_purchase_amount)
                final_amount = total_purchase_amount - discount_value
                return {"valid": True, "final_amount": final_amount, "discount_value": discount_value}
            elif hasattr(coupon, 'min_purchase_rule'):
                min_purchase_rule = coupon.min_purchase_rule
                reward = min_purchase_rule.apply_reward(total_purchase_amount)
                if reward['reward'] == 'discount':
                    final_amount = total_purchase_amount - reward['discount_value']
                    return {"valid": True, "final_amount": final_amount, "discount_value": reward['discount_value']}
                elif reward['reward'] == 'coins':
                    return {"valid": True, "final_amount": total_purchase_amount, "coins_awarded": reward['coins_awarded']}
            
            return {"valid": False, "message": "No applicable rule found."}
        else:
            return {"valid": False, "message": "Coupon is expired or not yet valid."}
    except Coupon.DoesNotExist:
        return {"valid": False, "message": "Invalid coupon code."}
  
    
# Apply Coupon API
class ApplyCouponAPI(APIView):
    def post(self, request):
        serializer = ApplyCouponSerializer(data=request.data)
        if serializer.is_valid():
            coupon_code = serializer.validated_data['coupon_code']
            total_purchase_amount = serializer.validated_data['total_price']
            business_name = serializer.validated_data['business_name']
            user = serializer.validated_data['cust_id']
            
            
            result = apply_coupon_logic(coupon_code, total_purchase_amount, business_name, user)
            
            if result['valid']:
                return Response({
                    'success': True,
                    'final_amount': result['final_amount'],
                    'discount_value': result['discount_value']
                })
            else:
                return Response({
                    'success': False,
                    'message': result['message']
                }, status=400)
        return Response(serializer.errors, status=400)

