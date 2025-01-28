from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_vendor, name='vendor_register'),
    path('login/', views.login_vendor, name='vendor_login'),
    path('logout/', views.logout_vendor, name='vendor_logout'),
    path('dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
]