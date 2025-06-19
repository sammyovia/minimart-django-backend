from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from orders import views

urlpatterns = [
    path('', views.OrderCreateView.as_view(), name='order-create'), 
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)