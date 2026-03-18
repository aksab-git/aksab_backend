from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from ..models.sales_rep import SalesRepresentative
from ..models.sales_manager import SalesManager

class LoginView(APIView):
    """
    تسجيل الدخول للمناديب والمشرفين وسحب بيانات العهدة (اللوجستيات)
    """
    def post(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')

        # 1. التحقق من المستخدم في Django Auth
        user = authenticate(username=phone, password=password)

        if user is not None:
            if not user.is_active:
                return Response({"message": "الحساب معطل، راجع الإدارة"}, status=status.HTTP_403_FORBIDDEN)

            response_data = {
                "status": "success",
                "user_id": user.id,
                "fullname": user.get_full_name() or user.username,
                "role": "unknown",
                "data": {}
            }

            # 2. تحديد نوع الحساب وسحب بيانات العهدة
            # هل هو مندوب؟
            if hasattr(user, 'sales_rep_profile'):
                profile = user.sales_rep_profile
                response_data["role"] = "sales_rep"
                response_data["data"] = {
                    "rep_code": profile.rep_code,
                    "insurance_points": float(profile.insurance_points),
                    "address": profile.address,
                    "phone": profile.phone
                }
            
            # هل هو مدير أو مشرف؟
            elif hasattr(user, 'sales_manager_profile'):
                profile = user.sales_manager_profile
                response_data["role"] = profile.role
                response_data["data"] = {
                    "role_display": profile.get_role_display(),
                    "phone": profile.phone,
                    "geographic_area": profile.geographic_area
                }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response({"status": "error", "message": "بيانات الدخول غير صحيحة"}, status=status.HTTP_401_UNAUTHORIZED)
