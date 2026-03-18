from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from ..models import SalesRepresentative

class LoginView(APIView):
    """
    مسؤول عن تسجيل دخول المنظومة (أكسب ERP)
    - يدعم دخول المناديب عبر رقم الهاتف.
    - يدعم دخول الإدارة عبر اسم المستخدم.
    - يقوم بتحديث الـ FCM Token لضمان وصول إشعارات العهدة.
    """
    def post(self, request):
        phone_input = request.data.get('phone')
        password_input = request.data.get('password')
        fcm_token = request.data.get('fcm_token') # استقبال التوكن الجديد من التطبيق

        try:
            # 1. البحث في سجلات مناديب المبيعات (اللوجستيات)
            rep = SalesRepresentative.objects.get(phone=phone_input)
            user = rep.user
            
            # التحقق من كلمة المرور وحالة الحساب
            if user.check_password(password_input):
                if not user.is_active:
                    return Response({
                        "status": "error", 
                        "message": "حساب المندوب معطل، يرجى مراجعة الإدارة"
                    }, status=status.HTTP_403_FOR_CONTENT_REPORT)
                
                # --- تحديث توكن الإشعارات (تأمين العهدة) ---
                if fcm_token:
                    rep.fcm_token = fcm_token
                    rep.save()

                # الرد ببيانات النجاح والمصطلحات اللوجستية الصريحة
                return Response({
                    "status": "success",
                    "role": "sales_rep",
                    "fullname": f"{user.first_name} {user.last_name}" if user.first_name else user.username,
                    "user_id": user.id,
                    "data": {
                        "rep_code": rep.rep_code,
                        "phone": rep.phone,
                        "insurance_points": str(rep.insurance_points), # تأمين عهدة الطلب الحالي
                    }
                })
            
        except SalesRepresentative.DoesNotExist:
            # 2. محاولة الدخول كإدارة (SuperAdmin) للمراجعة
            try:
                user = User.objects.get(username=phone_input)
                if user.check_password(password_input):
                    return Response({
                        "status": "success",
                        "role": "admin",
                        "fullname": "المدير العام للمنظومة",
                        "user_id": user.id,
                        "data": {}
                    })
            except User.DoesNotExist:
                pass

        # في حالة فشل كل المحاولات
        return Response({
            "status": "error", 
            "message": "بيانات الدخول غير صحيحة أو غير مسجلة بالمنظومة"
        }, status=status.HTTP_401_UNAUTHORIZED)

