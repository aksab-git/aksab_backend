from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from django.utils import timezone
from ..models.transactions import StockTransfer, TransferItem
from ..serializers import StockTransferSerializer 

class StockTransferViewSet(viewsets.ModelViewSet):
    """
    إدارة طلبات التحميل (Asset Management):
    تسمح للمندوب بإنشاء طلبات تحميل متعددة الأصناف، ومتابعة حالتها،
    وتأكيد استلام كل صنف على حدة (تأمين العهدة).
    """
    queryset = StockTransfer.objects.all().order_by('-created_at')
    serializer_class = StockTransferSerializer

    def get_queryset(self):
        """تصفية الطلبات: المندوب يشوف طلباته هو فقط بناءً على الكود أو الحالة"""
        queryset = super().get_queryset()
        rep_code = self.request.query_params.get('rep_code')
        status_param = self.request.query_params.get('status')
        
        if rep_code:
            queryset = queryset.filter(requested_by__rep_code=rep_code)
        if status_param:
            queryset = queryset.filter(status=status_param)
            
        return queryset

    def create(self, request, *args, **kwargs):
        """استقبال طلب تحميل عهدة جديد (متعدد الأصناف) من تطبيق المندوب"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                # توليد رقم إذن تلقائي (REQ + Timestamp) لضمان عدم التكرار
                if 'transfer_no' not in serializer.validated_data:
                    serializer.validated_data['transfer_no'] = f"REQ-{timezone.now().strftime('%Y%m%d%H%M%S')}"
                
                self.perform_create(serializer)
                return Response({
                    "message": "تم إرسال طلب تأمين العهدة بنجاح، في انتظار مراجعة الإدارة.",
                    "data": serializer.data
                }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'], url_path='confirm-item')
    def confirm_item_receipt(self, request, pk=None):
        """
        أكشن مخصص لتأكيد استلام صنف محدد (Checkbox) داخل إذن التحميل.
        يتم استدعاؤه من تطبيق المندوب عند 'تأكيد استلام الأمانات'.
        """
        transfer = self.get_object()
        item_id = request.data.get('item_id')

        # 🛡️ صمام أمان: لا يمكن تأكيد صنف إلا لو كانت حالة الإذن 'IN_TRANSIT'
        if transfer.status != 'IN_TRANSIT':
            return Response(
                {"error": "لا يمكن تأكيد استلام أصناف إلا بعد تحريك الشحنة (In Transit)."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # البحث عن الصنف داخل هذا الإذن تحديداً
            item = TransferItem.objects.get(id=item_id, transfer=transfer)
            
            with transaction.atomic():
                # تحديث حالة الصنف ليكون 'مستلم'
                item.is_received = True
                item.save()
                
                # 💡 فحص ذكي: لو كل الأصناف في الإذن تم استلامها، نغلق الإذن بالكامل تلقائياً
                all_items_received = not transfer.items.filter(is_received=False).exists()
                if all_items_received:
                    transfer.status = 'COMPLETED'
                    transfer.save()
                    # ملاحظة: حفظ الـ transfer هنا سيقوم أوتوماتيكياً بتحديث أرصدة المخازن (Logic في الموديل)

            return Response({
                "status": "success",
                "message": f"تم تأكيد استلام {item.product.name} في عهدتك بنجاح.",
                "overall_status": transfer.status,
                "is_fully_received": all_items_received
            }, status=status.HTTP_200_OK)

        except TransferItem.DoesNotExist:
            return Response({"error": "هذا الصنف غير موجود ضمن هذا الإذن."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
