from django.urls import path
from . import views

urlpatterns = [
    path('create-coupon/', views.create_coupon, name='create_coupon'),
    path('coupon-success/', views.coupon_success, name='coupon_success'),  # Add success view
     path('apply_coupon/', views.apply_coupon, name='apply_coupon'),
]