# from rest_framework import generics, status
# from rest_framework.response import Response
# from rest_framework.permissions import AllowAny, IsAuthenticated
# from django.contrib.auth import get_user_model

# from .serializers import UserRegisterSerializer, UserProfileSerializer

# User = get_user_model()

# class UserRegisterView(generics.CreateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserRegisterSerializer
#     permission_classes = [AllowAny] # Allow anyone to register

# class UserProfileView(generics.RetrieveUpdateAPIView):
#     queryset = User.objects.all()
#     serializer_class = UserProfileSerializer
#     permission_classes = [IsAuthenticated]

#     def get_object(self):
#         # Ensure users can only retrieve/update their own profile
#         return self.request.user

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404 # Import this!

from .serializers import UserRegisterSerializer, UserProfileSerializer

User = get_user_model()

class UserRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny] # Allow anyone to register

# View for the AUTHENTICATED USER'S OWN PROFILE
class MyProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # This correctly returns the currently authenticated user's profile
        # No 'pk' is needed in the URL for this view.
        return self.request.user

# (Optional) View for retrieving ANY user by ID (typically for Admins)
# Only add this if you explicitly need to fetch profiles of *other* users by ID.
# Be very careful with permissions here!
class UserDetailView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    # Only staff/admins should be able to view other users' profiles
    # Consider using a custom permission class here.
    # For now, let's keep it simple: IsAdminUser
    permission_classes = [IsAuthenticated] # For testing, change to IsAdminUser in production
    
    # get_object is not overridden, so it will use self.queryset and the pk from the URL
    # Example for admin access:
    # from rest_framework.permissions import IsAdminUser
    # permission_classes = [IsAdminUser]