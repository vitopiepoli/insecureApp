from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import VendorInvoice, Vendor, VendorPO
import mysql.connector
from django.db.models import Q
from django.urls import reverse
import hashlib
from django.utils import timezone
from django.contrib.auth import authenticate, login as django_login
from django.contrib.auth.decorators import login_required
from .decorators import user_role_required
from django.contrib.auth.models import Group
from django.contrib import messages
from django.db import DatabaseError
# Create your views here.




def home(request):
    return render(request, 'home.html')


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            django_login(request, user)
            if user.groups.filter(name='Admin').exists():
                return redirect('admin_invoices')
            elif user.groups.filter(name='Payable').exists():
                return redirect('payable_invoices')
            else:
                messages.error(request, "Unauthorized role")
                return render(request, 'home.html')
        else:
            messages.error(request, "Invalid credentials")
            return render(request, 'home.html')
    return render(request, 'home.html')


@login_required
@user_role_required(allowed_roles=['Admin'])
def admin_invoices(request):
    action = request.GET.get('action', 'view')
    if action == 'create':
        if request.method == 'POST':
            # Collect data from form
            vendor_id = request.POST.get('vendor_id')
            invoice_number = request.POST.get('invoice_number')
            invoice_date = request.POST.get('invoice_date')
            po_number = request.POST.get('purchase_order_number')
            description = request.POST.get('description')
            quantity = request.POST.get('quantity')
            price = request.POST.get('price')

            # Use Django ORM to create new VendorInvoice
            vendor, created = Vendor.objects.get_or_create(idVendors=vendor_id)
            po, created = VendorPO.objects.get_or_create(Purchase_Order_number=po_number)
            VendorInvoice.objects.create(
                vendor=vendor,
                Invoice_number=invoice_number,
                Invoice_date=invoice_date or timezone.now(),
                Purchase_Order=po,
                Description=description,
                Quantity=quantity,
                Price=price
            )
            return redirect('admin_invoices')
        return render(request, 'create_invoice.html')
    elif action in ['update', 'delete', 'view']:
        # Display invoices using admin credentials
        return render(request, 'admin_invoices.html', {'action': 'options'})

        
    
@login_required
@user_role_required(allowed_roles=['Payable'])
def payable_invoices(request):
    if request.method == 'GET' and any([request.GET.get('vendor_id'), request.GET.get('invoice_number'), request.GET.get('purchase_order_number')]):
        connection = mysql.connector.connect(
            host='localhost',
            user='payable@invoices',
            password='hardpass2',
            database='mydb'
        )
        cursor = connection.cursor(dictionary=True)

        vendor_id = request.GET.get('vendor_id', '')
        invoice_number = request.GET.get('invoice_number', '')
        po_number = request.GET.get('purchase_order_number', '')

        query = """
        SELECT * FROM vendor_invoices WHERE 1=1
        """
        params = []
        if vendor_id:
            query += " AND vendor_ID = %s"
            params.append(vendor_id)
        if invoice_number:
            query += " AND Invoice_number LIKE %s"
            params.append(f'%{invoice_number}%')
        if po_number:
            query += " AND Purchase_Order_number LIKE %s"
            params.append(f'%{po_number}%')

        cursor.execute(query, params)
        invoices = cursor.fetchall()
        cursor.close()
        connection.close()
    else:
        invoices = []

    return render(request, 'payable_invoices.html', {'invoices': invoices})