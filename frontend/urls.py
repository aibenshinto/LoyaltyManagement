from django.urls import path
from .views import coupon_page

urlpatterns = [
    path('', coupon_page, name='coupon_page'),
]