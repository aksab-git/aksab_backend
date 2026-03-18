from django.urls import path
from .views import LoginView

urlpatterns = [
    path('login/', LoginView.as_view(), name='api_login'),
]
from django.urls import path
from .views.auth_views import LoginView
from .views.work_day_views import WorkDayAPIView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('api/work-day/', WorkDayAPIView.as_view(), name='work_day_api'),
]

