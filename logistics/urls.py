from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.auth_views import LoginView
from .views.work_day_views import WorkDayAPIView

# استيراد الـ ViewSets الموجودة حالياً فقط
from .views import (
    MyInventoryViewSet, 
    MyTransfersViewSet, 
    StockTransferViewSet
    # تم حذف AllProductsViewSet لحل مشكلة الـ Import
)

# إعداد الـ Router
router = DefaultRouter()

# 1. جرد عهدة السيارة الحالي (البضاعة اللي معاه فعلياً)
router.register(r'my-inventory', MyInventoryViewSet, basename='my-inventory')

# 2. عرض التحويلات القديمة (للتوافق)
router.register(r'my-transfers', MyTransfersViewSet, basename='my-transfers')

# 3. نظام طلبات التحميل الجديد (إرسال طلب عهدة متعدد الأصناف)
router.register(r'stock-transfers', StockTransferViewSet, basename='stock-transfer')

urlpatterns = [
    # روابط الـ Auth والـ WorkDay
    path('login/', LoginView.as_view(), name='login'),
    path('work-day/', WorkDayAPIView.as_view(), name='work_day_api'),

    # دمج روابط الـ Router تلقائياً
    path('', include(router.urls)),
]
