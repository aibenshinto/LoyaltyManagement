from django.urls import path
from .views import VendorRegisterAPI, VendorLoginAPI, CreateCouponAPI, ApplyCouponAPI, TokenRefreshAPI

urlpatterns = [
    path('api/vendor/register/', VendorRegisterAPI.as_view(), name='vendor_register_api'),
    path('api/vendor/login/', VendorLoginAPI.as_view(), name='vendor_login_api'),
    path('api/coupons/create/', CreateCouponAPI.as_view(), name='create_coupon_api'),
    path('api/coupons/apply/', ApplyCouponAPI.as_view(), name='apply_coupon_api'),
    path('api/token/refresh/', TokenRefreshAPI.as_view(), name='token_refresh'),
]
