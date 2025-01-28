from django.urls import path
from .views import RequestCustomerDataView

urlpatterns = [
    path('api/customer-data/', RequestCustomerDataView.as_view(), name='request_customer_data'),
]
