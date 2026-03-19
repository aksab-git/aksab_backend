from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.auth_views import LoginView
from .views.work_day_views import WorkDayAPIView
from .views import MyInventoryViewSet, MyTransfersViewSet

# إعداد الـ Router للـ ViewSets (المخازن والتحويلات)
router = DefaultRouter()
router.register(r'my-inventory', MyInventoryViewSet, basename='my-inventory')
router.register(r'my-transfers', MyTransfersViewSet, basename='my-transfers')

urlpatterns = [
    # روابط الـ Auth والـ WorkDay (Class-based views)
    path('login/', LoginView.as_view(), name='login'),
    path('work-day/', WorkDayAPIView.as_view(), name='work_day_api'),
    
    # دمج روابط الـ Router (المخازن) تلقائياً
    path('', include(router.urls)),
]

