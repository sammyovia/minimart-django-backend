from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from products import views

urlpatterns = [
    path('', views.ProductList.as_view(), name='product-list'), 
    path('<int:pk>/', views.ProductDetail.as_view(), name='product-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)