from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from ..models.sales_representative import SalesRepresentative

class LoginView(APIView):
    def post(self, request):
        phone_input = request.data.get('phone')
        password_input = request.data.get('password')

        try:
            # 1. البحث عن المندوب برقم التليفون مباشرة من جدول المناديب
            rep = SalesRepresentative.objects.get(phone=phone_input)
            user = rep.user # الحصول على المستخدم المرتبط به

            # 2. التحقق من كلمة المرور
            if user.check_password(password_input):
                if not user.is_active:
                    return Response({"status": "error", "message": "الحساب معطل"}, status=403)
                
                return Response({
                    "status": "success",
                    "role": "sales_rep",
                    "fullname": user.get_full_name() or user.username,
                    "user_id": user.id,
                    "data": {
                        "rep_code": rep.rep_code,
                        "phone": rep.phone,
                        "insurance_points": str(rep.insurance_points),
                    }
                })
        except SalesRepresentative.DoesNotExist:
            # لو مالقاش مندوب، ممكن نجرب نشوف هل هو "أدمن" داخل بالـ username؟
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
