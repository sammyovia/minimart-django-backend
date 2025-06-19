from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product # Assuming products app is available
from paylater.models import PayLaterApplication

User = get_user_model()

class Order(models.Model):
    PAYMENT_OPTION_CHOICES = [
        ('OUTRIGHT', 'Pay Outright'),
        ('PAY_LATER_40', 'Pay Later (40% upfront)'),
        ('PAY_LATER_0', 'Pay Later (0% upfront)'),
    ]

    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending Payment'), # Order placed, payment pending (e.g., for 0% pay later or gateway redirect)
        ('PROCESSING', 'Processing'),   # Payment received, order being prepared
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),     # All payments made (for pay later), order delivered
        ('REFUNDED', 'Refunded'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('PARTIALLY_PAID', 'Partially Paid'), # For 40% upfront
        ('FULLY_REPAID', 'Fully Repaid'),     # For Pay Later 0% or 40% when remaining balance is paid
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50, choices=ORDER_STATUS_CHOICES, default='PENDING')
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS_CHOICES, default='PENDING')

    delivery_address = models.TextField()
    delivery_phone_number = models.CharField(max_length=20)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_option = models.CharField(max_length=20, choices=PAYMENT_OPTION_CHOICES)
    transaction_ref = models.CharField(max_length=255, blank=True, null=True,
                                     help_text="Reference from payment gateway for initial payment.")
    
    pay_later_application = models.ForeignKey(
        PayLaterApplication,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='related_orders',
        help_text="The approved Pay Later application used for this order."
    )
    instalment_paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                               help_text="Amount paid upfront for instalment option.")
    remaining_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00,
                                           help_text="Remaining amount to be paid for Pay Later.")
    repayment_due_date = models.DateField(null=True, blank=True,
                                         help_text="Date by which the remaining balance must be paid.")
    
    # For tracking multiple repayments for Pay Later (optional, more advanced)
    # You might have a separate `Repayment` model linked to Order for this.

    def __str__(self):
        return f"Order {self.id} by {self.user.username} - {self.status}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price of product at time of order")

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"