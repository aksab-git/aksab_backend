from django.urls import path
from .views import RegisterDelegateView, StoreListView

urlpatterns = [
    path('api/register/', RegisterDelegateView.as_view(), name='api-register'),
    path('api/stores/', StoreListView.as_view(), name='api-stores'),
]

