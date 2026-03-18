from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    # ده السطر اللي هيربط السيرفر بتطبيق اللوجستيات
    path('api/logistics/', include('logistics.urls')), 
]

