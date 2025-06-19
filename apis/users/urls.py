from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from users import views

urlpatterns = [
    path('', views.UserRegisterView.as_view(), name='register'), 
    path('<int:pk>/', views.UserProfileView.as_view(), name='product-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)