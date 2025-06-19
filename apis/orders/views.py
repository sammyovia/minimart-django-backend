from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from decimal import Decimal
from datetime import date, timedelta
from django.shortcuts import get_object_or_404

from products.models import Product
from paylater.models import PayLaterApplication
from .models import Order, OrderItem
from .serializers import OrderCreateSerializer, OrderDetailSerializer

class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        payment_option = serializer.validated_data['payment_option']
        items_data = serializer.validated_data['items']
        delivery_address = serializer.validated_data['delivery_address']
        delivery_phone_number = serializer.validated_data['delivery_phone_number']

        with transaction.atomic():
            total_amount = Decimal('0.00')
            order_items_to_create = []

            # Validate products and calculate total amount based on current prices
            for item_data in items_data:
                product = item_data['product'] # This is the Product object from serializer's PrimaryKeyRelatedField
                quantity = item_data['quantity']

                if product.stock < quantity:
                    return Response({"detail": f"Not enough stock for product {product.name}. Available: {product.stock}"},
                                    status=status.HTTP_400_BAD_REQUEST)

                total_amount += product.price * quantity
                order_items_to_create.append({
                    'product': product,
                    'quantity': quantity,
                    'price': product.price # Store price at time of order for historical accuracy
                })

            pay_later_app = None
            instalment_paid = Decimal('0.00')
            remaining_balance = Decimal('0.00')
            repayment_due_date = None
            payment_status = 'PENDING'
            order_initial_status = 'PENDING' # Default order status

            # --- Handle Pay Later Logic ---
            if payment_option in ['PAY_LATER_40', 'PAY_LATER_0']:
                try:
                    # Check if user has an APPROVED Pay Later application
                    pay_later_app = PayLaterApplication.objects.get(user=user, is_eligible=True, status='APPROVED_ELIGIBLE')
                except PayLaterApplication.DoesNotExist:
                    return Response({"detail": "User is not eligible for Pay Later. Please apply or wait for approval."},
                                    status=status.HTTP_403_FORBIDDEN)

                # Optional: Check if total_amount exceeds approved_credit_limit
                if pay_later_app.approved_credit_limit and total_amount > pay_later_app.approved_credit_limit:
                    return Response({
                        "detail": f"Order total (${total_amount:.2f}) exceeds your approved credit limit of ${pay_later_app.approved_credit_limit:.2f}."
                    }, status=status.HTTP_403_FORBIDDEN)

                if payment_option == 'PAY_LATER_40':
                    instalment_paid = total_amount * Decimal('0.40')
                    remaining_balance = total_amount - instalment_paid
                    
                    # --- Integrate with Payment Gateway for 40% upfront ---
                    # In a real scenario, this would call your payment gateway API
                    # (e.g., Paystack, Stripe) to initiate payment.
                    # This step might involve redirecting the user or waiting for a webhook.
                    # For now, we simulate success.
                    payment_success = self._initiate_payment(user, instalment_paid, "40% upfront instalment")
                    if not payment_success:
                        return Response({"detail": "Failed to process 40% instalment payment. Please try again."},
                                        status=status.HTTP_400_BAD_REQUEST)
                    payment_status = 'PARTIALLY_PAID'
                    order_initial_status = 'PROCESSING' # Order can proceed once upfront payment is made

                else: # PAY_LATER_0
                    remaining_balance = total_amount
                    payment_status = 'PENDING' # No upfront payment
                    order_initial_status = 'PENDING' # Order remains pending until first payment

                # Calculate repayment due date (e.g., 30 days from now)
                repayment_due_date = date.today() + timedelta(days=30)
            
            else: # OUTRIGHT payment
                # --- Integrate with Payment Gateway for full payment ---
                payment_success = self._initiate_payment(user, total_amount, "Full payment")
                if not payment_success:
                    return Response({"detail": "Failed to process full payment. Please try again."},
                                    status=status.HTTP_400_BAD_REQUEST)
                payment_status = 'PAID'
                order_initial_status = 'PROCESSING' # Order can proceed as it's fully paid

            # Create the Order
            order = Order.objects.create(
                user=user,
                total_amount=total_amount,
                payment_option=payment_option,
                delivery_address=delivery_address,
                delivery_phone_number=delivery_phone_number,
                payment_status=payment_status,
                pay_later_application=pay_later_app,
                instalment_paid_amount=instalment_paid,
                remaining_balance=remaining_balance,
                repayment_due_date=repayment_due_date,
                status=order_initial_status
            )

            # Create Order Items and reduce product stock
            for item_data in order_items_to_create:
                OrderItem.objects.create(
                    order=order,
                    product=item_data['product'],
                    quantity=item_data['quantity'],
                    price=item_data['price'] # This is the price at time of order
                )
                # Reduce product stock
                item_data['product'].stock -= item_data['quantity']
                item_data['product'].save()

            # Return the created order details
            headers = self.get_success_headers(OrderDetailSerializer(order).data)
            return Response(OrderDetailSerializer(order).data, status=status.HTTP_201_CREATED, headers=headers)

    # Placeholder for actual payment gateway integration
    def _initiate_payment(self, user, amount, description):
        """
        This method would integrate with your chosen payment gateway (e.g., Paystack, Stripe).
        It would involve:
        1. Calling the payment gateway's API to initialize a transaction.
        2. In a real application, you might return a payment URL to the frontend
           or specific tokens that the frontend uses to open a payment widget.
        3. A webhook from the payment gateway would then update the Order's payment_status.

        For this example, we just simulate success.
        """
        print(f"Simulating payment initiation for user {user.username}, amount {amount}, for: {description}")
        # In a real scenario, this would be a complex interaction
        # For now, assume it always succeeds for the purpose of backend logic flow
        return True

class OrderListView(generics.ListAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Users can only see their own orders
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all() # Used for lookup, but get_object will filter by user

    def get_object(self):
        # Ensure users can only retrieve their own specific order
        return get_object_or_404(Order, pk=self.kwargs['pk'], user=self.request.user)