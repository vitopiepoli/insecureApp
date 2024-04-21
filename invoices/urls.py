from django.urls import path
from . import views  # Correct relative import since it's within the same app

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('admin_invoices/', views.admin_invoices, name='admin_invoices'),
    path('payable_invoices/', views.payable_invoices, name='payable_invoices'),
]