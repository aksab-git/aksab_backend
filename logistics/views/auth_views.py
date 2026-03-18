from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from ..models import SalesRepresentative 

class LoginView(APIView):
    def post(self, request):
        phone_input = request.data.get('phone')
        password_input = request.data.get('password')

        try:
            # البحث برقم الهاتف في بروفايل المندوب (حقل phone في موديل SalesRepresentative)
            rep = SalesRepresentative.objects.get(phone=phone_input)
            user = rep.user

            if user.check_password(password_input):
                if not user.is_active:
                    return Response({"status": "error", "message": "الحساب معطل"}, status=403)
                
                return Response({
                    "status": "success",
                    "role": "sales_rep",
                    "fullname": f"{user.first_name} {user.last_name}" if user.first_name else user.username,
                    "user_id": user.id,
                    "data": {
                        "rep_code": rep.rep_code,
                        "phone": rep.phone,
                        "insurance_points": str(rep.insurance_points), # تأمين عهدة الطلب
                    }
                })
        except SalesRepresentative.DoesNotExist:
            # محاولة دخول كـ SuperAdmin بالـ Username (للمديرين)
            try:
                user = User.objects.get(username=phone_input)
                if user.check_password(password_input):
                    return Response({
                        "status": "success",
                        "role": "admin",
                        "fullname": "المدير العام",
                        "user_id": user.id,
                        "data": {}
                    })
            except User.DoesNotExist:
                pass

        return Response({"status": "error", "message": "بيانات الدخول غير صحيحة"}, status=401)
