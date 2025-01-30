from django.urls import path
from .import views

urlpatterns = [
    path('api/customer-data/', views.RequestCustomerDataView.as_view(), name='request_customer_data'),
    path('loyalty_configuration/', views.loyalty_config, name='loyalty_configuration'),
    path('api/purchase-data/', views.PurchaseRewardsView.as_view(), name='purchase_customer_data'),
    path('api/redeem-coin/',views.RequestCustomerRedeemView.as_view(),name='redeem-coin'),
    
]