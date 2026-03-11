from django.urls import path
from . import views

urlpatterns = [
    path('', views.InvoiceListView.as_view(), name='invoice_list'),
    path('<int:pk>/edit/', views.InvoiceUpdateView.as_view(), name='invoice_edit'),
    path('<int:pk>/pay/', views.mark_paid, name='mark_paid'),
]
