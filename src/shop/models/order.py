from base.models import BaseModel
from django.db import models
from shop.models.shop import Shop
from shop.models.product import Product
import uuid


class Order(BaseModel):
    SHIPPING_STATUS_CHOICES = [
        ('0', 'Not Shipped'),
        ('1', 'Processing'),
        ('2', 'Shipped'),
        ('3', 'In Transit'),
        ('4', 'Out for Delivery'),
        ('5', 'Delivered'),
        ('6', 'Returned'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('0', 'Pending'),
        ('1', 'Completed'),
        ('2', 'Failed'),
        ('3', 'Refunded'),
    ]

    order_number = models.CharField(
        max_length=100,
        unique=True,
        default=uuid.uuid4,  # Generates a new UUID automatically
        editable=False       # Prevents changing it via admin/forms
    )
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='orders')
    customer_name = models.CharField(max_length=100, unique=True)
    customer_number = models.CharField(max_length=200)
    customer_message = models.TextField(null=True, blank=True)
    shipping_address = models.TextField()
    
    shipping_status = models.CharField(max_length=1, choices=SHIPPING_STATUS_CHOICES, default='0')
    payment_status = models.CharField(max_length=1, choices=PAYMENT_STATUS_CHOICES, default='0')

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Order {self.order_number} by {self.customer_name}'
    


class OrderProduct(BaseModel):
    STATUS_CHOICES = [
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]

    order_obj = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    product_obj = models.ForeignKey(Product, on_delete=models.CASCADE)

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='accepted')
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    declined_at = models.DateTimeField(help_text="Only if this product is declined", blank=True, null=True) 

    def __str__(self):
        return f'{self.quantity} of {self.product_obj.name} in order {self.order_obj.order_number}'