from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import VendorInvoice, Vendor, VendorPO
import mysql.connector
from django.db.models import Q
from django.urls import reverse
import hashlib
# Create your views here.

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


user_credentials = {
    "admin@invoices": "hardpass",
    "payable@invoices": "hardpass2",
}

def home(request):
    return render(request, 'home.html')


def login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    
    if user_credentials.get(username) == password:
        user_type = request.POST.get('user_type')
        if user_type == 'Admin':
            return redirect(reverse('admin_invoices'))
        elif user_type == 'Payable':
            return redirect(reverse('payable_invoices'))
    return HttpResponse("Invalid credentials")

def admin_invoices(request):
    action = request.GET.get('action', 'view')
    if action == 'create':
        if request.method == 'POST':
            # Connect using admin credentials
            connection = mysql.connector.connect(
                host='localhost',
                user='admin@invoices',
                password='hardpass',
                database='mydb'
            )
            cursor = connection.cursor()

            # Collect data from form
            vendor_id = request.POST.get('vendor_id')
            invoice_number = request.POST.get('invoice_number')
            invoice_date = request.POST.get('invoice_date')
            po_number = request.POST.get('purchase_order_number')
            description = request.POST.get('description')
            quantity = request.POST.get('quantity')
            price = request.POST.get('price')
            
            vendor, created = Vendor.objects.get_or_create(idVendors=vendor_id)
            po, created = VendorPO.objects.get_or_create(Purchase_Order_number=po_number)

            # SQL to insert data
            insert_query = """
            INSERT INTO vendor_invoices (vendor_ID, Invoice_number, Invoice_date, Purchase_Order_number, Description, Quantity, Price)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (vendor_id, invoice_number, invoice_date, po_number, description, quantity, price))
            connection.commit()
            cursor.close()
            connection.close()
            return redirect('admin_invoices')
        return render(request, 'create_invoice.html')
    elif action in ['update', 'delete', 'view']:
        # Display invoices using admin credentials
        return render(request, 'admin_invoices.html', {'action': 'options'})
        
    

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