from django.urls import path
from .views import CustomerRegisterView, ProductListView, LoginView, LogoutView, add_to_cart, cart_view, checkout_view

urlpatterns = [
    path('register/', CustomerRegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add-to-cart'),
    path('cart/', cart_view, name='cart'),  # Cart view should display the cart items
    path('checkout/', checkout_view, name='checkout'),
]
