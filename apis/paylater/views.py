from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import ObjectDoesNotExist # Import for specific exception handling

from .models import PayLaterApplication
from .serializers import PayLaterApplicationSerializer, PayLaterEligibilitySerializer
from .tasks import perform_crc_check_task

class PayLaterApplicationCreateView(generics.CreateAPIView):
    queryset = PayLaterApplication.objects.all()
    serializer_class = PayLaterApplicationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        # Check if an application already exists for the user
        try:
            existing_app = PayLaterApplication.objects.get(user=request.user)
            # If an application exists, return its current status
            return Response(
                PayLaterEligibilitySerializer(existing_app).data,
                status=status.HTTP_200_OK # Or HTTP_409_CONFLICT if you want to explicitly signal
            )
        except ObjectDoesNotExist:
            pass # No existing application, proceed to create

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        application = serializer.save()
        
        # Trigger the asynchronous CRC check
        perform_crc_check_task.delay(application.id)
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PayLaterEligibilityRetrieveView(generics.RetrieveAPIView):
    """
    Allows an authenticated user to check the status and eligibility of their Pay Later application.
    """
    serializer_class = PayLaterEligibilitySerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Ensure users can only check their own application
        try:
            return PayLaterApplication.objects.get(user=self.request.user)
        except PayLaterApplication.DoesNotExist:
            raise status.HTTP_404_NOT_FOUND({"detail": "No Pay Later application found for this user."})