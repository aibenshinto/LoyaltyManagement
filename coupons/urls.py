from django.urls import path
from .views import  CreateCouponAPI, ApplyCouponAPI

urlpatterns = [

    path('api/coupons/create/', CreateCouponAPI.as_view(), name='create_coupon_api'),
    path('api/coupons/apply/', ApplyCouponAPI.as_view(), name='apply_coupon_api'),

]
