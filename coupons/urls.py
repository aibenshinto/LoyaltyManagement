from django.urls import path
from .views import  ApplyCouponAPI
from . import views
urlpatterns = [

    path('create-coupon/', views.create_coupon_view, name='create_coupon'),
    path('api/coupons/apply/', ApplyCouponAPI.as_view(), name='apply_coupon_api'),

]

