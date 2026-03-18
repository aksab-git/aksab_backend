# logistics/views/auth_views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.db import transaction

class RegisterDelegateView(APIView):
    """
    استقبال طلبات انضمام المناديب والمشرفين (تحويل من Firebase)
    """
    @transaction.atomic
    def post(self, request):
        data = request.data
        try:
            phone = data.get('phone')
            password = data.get('password')
            fullname = data.get('fullname')
            role = data.get('role')
            address = data.get('address')

            # 1. إنشاء المستخدم الأساسي (حالة غير نشط لانتظار الموافقة)
            user = User.objects.create_user(
                username=phone, # الهاتف هو المعرف الفريد
                password=password,
                first_name=fullname,
                is_active=False 
            )

            # 2. هنا مستقبلاً هنربطه بجدول الـ Profile لتخزين (نقاط التأمين - insurance_points)
            # و الـ Role الوظيفي بشكل رسمي
            
            return Response({
                "status": "success",
                "message": "تم استلام طلب العهدة بنجاح، في انتظار تفعيل الإدارة"
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

