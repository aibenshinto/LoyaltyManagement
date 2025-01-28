<<<<<<< HEAD
from django.urls import path
from .views import VendorRegisterAPI, VendorLoginAPI, CreateCouponAPI, ApplyCouponAPI, TokenRefreshAPI

urlpatterns = [
    path('api/vendor/register/', VendorRegisterAPI.as_view(), name='vendor_register_api'),
    path('api/vendor/login/', VendorLoginAPI.as_view(), name='vendor_login_api'),
    path('api/coupons/create/', CreateCouponAPI.as_view(), name='create_coupon_api'),
    path('api/coupons/apply/', ApplyCouponAPI.as_view(), name='apply_coupon_api'),
    path('api/token/refresh/', TokenRefreshAPI.as_view(), name='token_refresh'),
]
=======
from django.urls import path
from .views import  ApplyCouponAPI
from . import views
urlpatterns = [

    path('create-coupon/', views.create_coupon_view, name='create_coupon'),
    path('api/coupons/apply/', ApplyCouponAPI.as_view(), name='apply_coupon_api'),

]
>>>>>>> 50b8c76e58e92ff6883a001f74cad939c4d001e7
