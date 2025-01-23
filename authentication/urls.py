from django.urls import path
from . import views

urlpatterns = [
    path('vendor/register/', views.RegisterVendorView.as_view(), name='register_vendor'),# Vendor Registration
    path('vendor/login/', views.VendorLoginView.as_view(), name='vendor_login'),# Vendor Login
    path('vendor/dashboard/', views.VendorDashboardView.as_view(), name='vendor_dashboard'),#Vendor Dashboard
    path('logout/', views.VendorLogoutView.as_view(), name='logout'), #Logout
]
