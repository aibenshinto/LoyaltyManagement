from django.urls import path
from .views import  CreateCouponAPI, ApplyCouponAPI,VendorRegistrationAPIView,VendorLoginAPIView

urlpatterns = [
    
     path('register/', VendorRegistrationAPIView.as_view(), name='vendor-register'),
    path('login/', VendorLoginAPIView.as_view(), name='vendor-login'),

    path('api/coupons/create/', CreateCouponAPI.as_view(), name='create_coupon_api'),
    path('api/coupons/apply/', ApplyCouponAPI.as_view(), name='apply_coupon_api'),

]
