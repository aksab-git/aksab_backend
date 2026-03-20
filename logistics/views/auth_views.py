from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token  # ⬅️ سطر جديد (مهم جداً)
from ..models import SalesRepresentative

class LoginView(APIView):
    def post(self, request):
        phone_input = request.data.get('phone')
        password_input = request.data.get('password')
        fcm_token = request.data.get('fcm_token')

        try:
            # 1. البحث في سجلات مناديب المبيعات
            rep = SalesRepresentative.objects.get(phone=phone_input)
            user = rep.user
            
            if user.check_password(password_input):
                if not user.is_active:
                    return Response({
                        "status": "error", 
                        "message": "حساب المندوب معطل، يرجى مراجعة الإدارة"
                    }, status=status.HTTP_403_FORBIDDEN)
                
                # --- توليد/جلب التوكن الخاص بالمندوب ---
                token, _ = Token.objects.get_or_create(user=user) # ⬅️ سطر جديد

                if fcm_token:
                    rep.fcm_token = fcm_token
                    rep.save()

                return Response({
                    "status": "success",
                    "token": token.key,  # 🔑 إرسال التوكن للموبايل
                    "role": "sales_rep",
                    "fullname": f"{user.first_name} {user.last_name}" if user.first_name else user.username,
                    "user_id": user.id,
                    "data": {
                        "rep_code": rep.rep_code,
                        "phone": rep.phone,
                        "insurance_points": str(rep.insurance_points),
                    }
                })
            
        except SalesRepresentative.DoesNotExist:
            # 2. محاولة الدخول كإدارة (SuperAdmin)
            try:
                user = User.objects.get(username=phone_input)
                if user.check_password(password_input):
                    # --- توليد/جلب التوكن الخاص بالمدير ---
                    token, _ = Token.objects.get_or_create(user=user) # ⬅️ سطر جديد
                    
                    return Response({
                        "status": "success",
                        "token": token.key,  # 🔑 إرسال التوكن للمدير أيضاً
                        "role": "admin",
                        "fullname": "المدير العام للمنظومة",
                        "user_id": user.id,
                        "data": {}
                    })
            except User.DoesNotExist:
                pass

        return Response({
            "status": "error", 
            "message": "بيانات الدخول غير صحيحة أو غير مسجلة بالمنظومة"
        }, status=status.HTTP_401_UNAUTHORIZED)
