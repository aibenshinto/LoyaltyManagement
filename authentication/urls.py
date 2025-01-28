<<<<<<< HEAD
from django.urls import path
from . import views

urlpatterns = [
    path('vendor/register/', views.RegisterVendorView.as_view(), name='register_vendor'),# Vendor Registration
    path('vendor/login/', views.VendorLoginView.as_view(), name='vendor_login'),# Vendor Login
    path('vendor/dashboard/', views.VendorDashboardView.as_view(), name='vendor_dashboard'),#Vendor Dashboard
    path('logout/', views.VendorLogoutView.as_view(), name='logout'), #Logout
]
=======
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_vendor, name='vendor_register'),
    path('login/', views.login_vendor, name='vendor_login'),
    path('logout/', views.logout_vendor, name='vendor_logout'),
    path('dashboard/', views.vendor_dashboard, name='vendor_dashboard'),
]
>>>>>>> 50b8c76e58e92ff6883a001f74cad939c4d001e7
