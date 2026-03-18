from django.urls import path
from .views.auth_views import RegisterDelegateView

urlpatterns = [
    path('register/', RegisterDelegateView.as_view(), name='register_delegate'),
]

