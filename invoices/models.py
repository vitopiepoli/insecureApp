from django.db import models

# Create your models here.
class Vendor(models.Model):
    idVendors = models.AutoField(primary_key=True)
    Name = models.CharField(max_length=45)
    Address = models.CharField(max_length=45)

class VendorPO(models.Model):
    Purchase_Order_number = models.CharField(max_length=20, primary_key=True)
    PO_issuer_ID = models.IntegerField()
    PO_approver_ID = models.IntegerField()
    Date_issued = models.DateField()
    Date_approved = models.DateField()

class VendorInvoice(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    Invoice_number = models.CharField(max_length=45, primary_key=True)
    Invoice_date = models.DateField()
    Purchase_Order = models.ForeignKey(VendorPO, on_delete=models.CASCADE)
    Description = models.CharField(max_length=45)
    Quantity = models.IntegerField()
    Price = models.DecimalField(max_digits=11, decimal_places=2)