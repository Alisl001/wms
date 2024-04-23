from django.db import models
from django.contrib.auth.models import User

# 1. User model default in django but this is for staff permission.
class StaffPermission(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_permission')
    is_permitted = models.BooleanField(default=False)


# 2. Product model:
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE)
    size = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    barcode = models.CharField(max_length=50, unique=True)
    photo = models.ImageField(upload_to='product_photos/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.barcode}"


# 3. Category model:
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    def __str__(self):
        return f"{self.name}"


# 4. Supplier model:
class Supplier(models.Model):
    name = models.CharField(max_length=100)
    contact_person = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    photo = models.ImageField(upload_to='supplier_photos/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.name}"


# 5. Warehouse model:
class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.name}"


# 6. Shelf model:
class Shelf(models.Model):
    warehouse = models.ForeignKey('Warehouse', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    barcode = models.CharField(max_length=50, unique=True)
    capacity = models.IntegerField()
    def __str__(self):
        return f"{self.name} ({self.barcode}) - Capacity: {self.capacity}"


# 7. Inventory model:
class Inventory(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    shelf = models.ForeignKey('Shelf', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    expiry_date = models.DateField()
    status_choices = [
        ('available', 'Available'),
        ('nearly_expiring', 'Nearly Expiring'),
        ('expired', 'Expired'),
    ]
    status = models.CharField(max_length=20, choices=status_choices)


# 8. Shipment model:
class Shipment(models.Model):
    supplier = models.ForeignKey('Supplier', on_delete=models.CASCADE)
    arrival_date = models.DateField()
    receive_date = models.DateField()
    status_choices = [
        ('pending', 'Pending'),
        ('received', 'Received'),
    ]
    status = models.CharField(max_length=20, choices=status_choices)
    def __str__(self):
        return f"Shipment from {self.supplier.name} - Status: {self.status}"


# 9. ShipmentDetail model:
class ShipmentDetail(models.Model):
    shipment = models.ForeignKey('Shipment', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    status_choices = [
        ('pending', 'Pending'),
        ('received', 'Received'),
        ('put_away', 'Put Away'),
    ]
    status = models.CharField(max_length=20, choices=status_choices)
    def __str__(self):
        return f"Detail {self.id} of Shipment {self.shipment.id} - Product: {self.product.name}"


# 10. Order model:
class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    priority_choices = [
        ('high', 'High'),
        ('low', 'Low'),
    ]
    priority = models.CharField(max_length=20, choices=priority_choices)
    status_choices = [
        ('pending', 'Pending'),
        ('picked', 'Picked'),
        ('packed', 'Packed'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=status_choices)
    def __str__(self):
        return f"Order {self.id} by {self.customer.username} - Total: ${self.total_price}"


# 11. OrderDetail model:
class OrderDetail(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    status_choices = [
        ('pending', 'Pending'),
        ('picked', 'Picked'),
        ('packed', 'Packed'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=status_choices)


# 12. Activity model:
class Activity(models.Model):
    staff = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    activity_type_choices = [
        ('put_away', 'Put Away'),
        ('pick', 'Pick'),
        ('receive', 'Receive'),
        ('other', 'Other'),
    ]
    activity_type = models.CharField(max_length=20, choices=activity_type_choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.activity_type} by {self.staff.username} on {self.timestamp.strftime('%Y-%m-%d %H:%M')}"


# 13. Favorite model:
class Favorite(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)


# 14. Report model: 
class Report(models.Model):
    report_type_choices = [
        ('sales', 'Sales Report'),
        ('inventory', 'Inventory Report'),
        ('activity', 'Activity Report'),
        ('other', 'Other Report'),
    ]
    report_type = models.CharField(max_length=20, choices=report_type_choices)
    generated_at = models.DateTimeField(auto_now_add=True)
    data = models.JSONField()
    def __str__(self):
        return f"{self.report_type} generated on {self.generated_at.strftime('%Y-%m-%d')}"



# 15. Notification model:
class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status_choices = [
        ('unread', 'Unread'),
        ('read', 'Read'),
    ]
    status = models.CharField(max_length=20, choices=status_choices)
    


# 16. BarcodeScanning model:
class BarcodeScanning(models.Model):
    scanned_by = models.ForeignKey(User, on_delete=models.CASCADE)
    scanned_item = models.ForeignKey('Product', on_delete=models.CASCADE)
    shelf = models.ForeignKey('Shelf', on_delete=models.CASCADE)
    action_choices = [
        ('put_away', 'Put Away'),
        ('pick', 'Pick'),
        ('receive', 'Receive'),
    ]
    action = models.CharField(max_length=20, choices=action_choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.action} of {self.scanned_item.name} by {self.scanned_by.username} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"



# 17. Wallet model:
class Wallet(models.Model):
    customer = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
            return f"Wallet of {self.customer.username} - Balance: ${self.balance}"


# 18. TransactionLog model:
class TransactionLog(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('purchase', 'Purchase'),
        ('refund', 'Refund'),
    ]
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction #{self.id} - User: {self.customer.username} - Type: {self.transaction_type} - Amount: {self.amount}"




