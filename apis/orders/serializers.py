from rest_framework import serializers
from .models import Order, OrderItem
from products.models import Product

class OrderItemSerializer(serializers.ModelSerializer):
    # For incoming data from frontend, expect product_id
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product')
    # For outgoing data (read-only), show product name and current price
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_current_price = serializers.DecimalField(source='product.price', max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product_id', 'product_name', 'product_current_price', 'quantity']
        # The 'price' field in OrderItem model is set by backend at time of order.
        # It's not exposed for direct write from frontend.

class OrderCreateSerializer(serializers.Serializer):
    # Frontend sends: payment option, delivery details, and list of items
    payment_option = serializers.ChoiceField(choices=Order.PAYMENT_OPTION_CHOICES)
    delivery_address = serializers.CharField(max_length=500)
    delivery_phone_number = serializers.CharField(max_length=20)
    items = OrderItemSerializer(many=True, write_only=True)

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError("Order must contain at least one item.")
        for item_data in items:
            if item_data['quantity'] <= 0:
                raise serializers.ValidationError("Quantity must be positive for all items.")
        return items

class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True) # Nested serializer for order items
    user = serializers.StringRelatedField(read_only=True) # Shows username
    pay_later_application_status = serializers.CharField(
        source='pay_later_application.status', read_only=True, allow_null=True
    )
    pay_later_approved_limit = serializers.DecimalField(
        source='pay_later_application.approved_credit_limit', max_digits=12, decimal_places=2, read_only=True, allow_null=True
    )

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'created_at', 'updated_at', 'status', 'payment_status',
            'delivery_address', 'delivery_phone_number', 'total_amount',
            'payment_option', 'transaction_ref', 'items',
            'instalment_paid_amount', 'remaining_balance', 'repayment_due_date',
            'pay_later_application_status', 'pay_later_approved_limit'
        ]
        read_only_fields = fields # All fields are read-only when viewing an existing order