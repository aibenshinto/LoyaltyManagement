from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import Coupon,Vendor
from .serializers import ApplyCouponSerializer, CouponSerializer, DiscountCouponSerializer, MinPurchaseCouponSerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from rest_framework_simplejwt.authentication import JWTAuthentication
from wallet.models import CustomerVendor
from rest_framework.renderers import TemplateHTMLRenderer


# API to Create Coupons
class CreateCouponAPI(APIView):
    renderer_classes = [TemplateHTMLRenderer]
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    template_name = 'create_coupon.html'
    
    def get(self, request):
        print(request.headers)
        return Response({}, template_name=self.template_name) 

    def post(self, request):
        coupon_type = request.data.get('coupon_type', '')
        
        try:
            vendor = Vendor.objects.get(user=request.user)
        except Vendor.DoesNotExist:
            return Response({"message": "Vendor not found for the current user."}, status=status.HTTP_400_BAD_REQUEST)


        coupon_serializer = CouponSerializer(data=request.data, context={'request': request})
        if coupon_serializer.is_valid():
            coupon = coupon_serializer.save(vendor=vendor)

            if coupon_type == 'discount':
                discount_serializer = DiscountCouponSerializer(data=request.data, context={'request': request})
                if discount_serializer.is_valid():
                    discount_coupon = discount_serializer.save(coupon=coupon)
                    return Response({"message": "Discount coupon created successfully"}, status=status.HTTP_201_CREATED)
            elif coupon_type == 'min_purchase':
                min_purchase_serializer = MinPurchaseCouponSerializer(data=request.data, context={'request': request})
                if min_purchase_serializer.is_valid():
                    min_purchase_coupon = min_purchase_serializer.save(coupon=coupon)
                    return Response({"message": "Min Purchase coupon created successfully"}, status=status.HTTP_201_CREATED)
            
            
        return Response(coupon_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Apply Coupon Logic
def apply_coupon_logic(coupon_code, total_purchase_amount, vendor_key, user):
    try:
        coupon = Coupon.objects.get(code=coupon_code,vendor = vendor_key)
        
        if not CustomerVendor.objects.filter(customerid=user, vendorkey=vendor_key).exists():
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
            vendor_key = serializer.validated_data['vendor_key']
            user = serializer.validated_data['cust_id']
            
            
            result = apply_coupon_logic(coupon_code, total_purchase_amount, vendor_key, user)
            
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
