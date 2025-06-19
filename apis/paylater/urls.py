from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from paylater import views

urlpatterns = [
    path('', views.PayLaterApplicationCreateView.as_view(), name='pay_later_apply'), 
    path('<int:pk>/', views.PayLaterEligibilityRetrieveView.as_view(), name='pay_later_eligibility'),
]

urlpatterns = format_suffix_patterns(urlpatterns)