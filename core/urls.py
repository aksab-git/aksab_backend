from django.urls import path
from .views.auth_views import RegisterDelegateView # استدعاء مباشر من الملف

urlpatterns = [
    # هنشغل دي بس دلوقتي عشان نتأكد إن السيرفر ققام
    path('register/', RegisterDelegateView.as_view(), name='register_delegate'),
]

