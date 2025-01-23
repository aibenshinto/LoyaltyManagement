from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status
from django.utils import timezone
from .models import Coupon
from .serializers import ApplyCouponSerializer, CouponSerializer, DiscountCouponSerializer, BOGOCouponSerializer
from .models import Vendor
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import render
from rest_framework_simplejwt.authentication import JWTAuthentication


# API to Create Coupons
class CreateCouponAPI(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    
    def get(self, request):
        return render(request, 'create_coupon.html') 

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
            elif coupon_type == 'bogo':
                bogo_serializer = BOGOCouponSerializer(data=request.data, context={'request': request})
                if bogo_serializer.is_valid():
                    bogo_coupon = bogo_serializer.save(coupon=coupon)
                    return Response({"message": "BOGO coupon created successfully"}, status=status.HTTP_201_CREATED)
            
        return Response(coupon_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Apply Coupon Logic
def apply_coupon_logic(coupon_code, total_purchase_amount, vendor_key, user):
    try:
        coupon = Coupon.objects.get(code=coupon_code,vendor = vendor_key)
        
        if not Customer.objects.filter(user=user, vendor=coupon.vendor).exists():
                return {"valid": False, "message": "You are not a customer of this vendor."}
        
        if coupon.valid_from <= timezone.now() <= coupon.valid_until:
            # Check for the type of coupon and apply corresponding rules
            if hasattr(coupon, 'discount_rule'):
                discount_rule = coupon.discount_rule  # Related rule for discount coupon
                discount_value = discount_rule.get_discount_value(total_purchase_amount)
                final_amount = total_purchase_amount - discount_value
                return {"valid": True, "final_amount": final_amount, "discount_value": discount_value}

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
            user = request.user 
            
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
