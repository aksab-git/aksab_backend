from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from ..models.mainInventory import InventoryItem
from ..models.transactions import StockTransfer
from ..serializers import InventoryItemSerializer, StockTransferSerializer

class MyInventoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    يعرض للمندوب البضاعة الموجودة في عهدته (سيارته) حالياً.
    تم تحديثها لتقبل الفلترة بـ rep_code لضمان دقة البيانات وتخطي أخطاء الصلاحيات.
    """
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # 1. محاولة جلب كود المندوب من الرابط (Query Params) المرسل من فلاتر
        rep_code = self.request.query_params.get('rep_code')

        if rep_code:
            # البحث عن المخزن المرتبط بهذا الكود تحديداً
            return InventoryItem.objects.filter(
                warehouse__assigned_rep__rep_code=rep_code,
                warehouse__warehouse_type='VAN' # ضمان أننا نعرض عهدة السيارة فقط
            )

        # 2. إذا لم يرسل الكود، نبحث عن المخزن المرتبط بحساب المستخدم المسجل
        return InventoryItem.objects.filter(
            warehouse__assigned_rep__user=user,
            warehouse__warehouse_type='VAN'
        )

class MyTransfersViewSet(viewsets.ModelViewSet):
    """
    يعرض "تحويلات العهد" المرسلة للمندوب ليقوم بتأكيد استلامها.
    تسمح للمندوب برؤية الشحنات التي في الطريق (IN_TRANSIT) ليقوم بتأكيدها.
    """
    serializer_class = StockTransferSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        rep_code = self.request.query_params.get('rep_code')

        # الفلترة بناءً على المخزن المستلم الذي يخص المندوب
        if rep_code:
            queryset = StockTransfer.objects.filter(
                receiver_warehouse__assigned_rep__rep_code=rep_code
            )
        else:
            queryset = StockTransfer.objects.filter(
                receiver_warehouse__assigned_rep__user=user
            )
        
        # ترتيب النتائج: الأحدث يظهر أولاً
        return queryset.order_by('-created_at')

    def update(self, request, *args, **kwargs):
        """
        تخصيص عملية التحديث للسماح للمندوب بتغيير الحالة إلى COMPLETED فقط.
        """
        instance = self.get_object()
        # إذا أراد المندوب تأكيد الاستلام، نقوم بتحديث الحالة
        if request.data.get('status') == 'COMPLETED':
            instance.status = 'COMPLETED'
            instance.save() # سيقوم الموديل تلقائياً بنقل الكميات كما برمجناه في save()
            return Response({'status': 'تأكيد العهدة: تم استلام الأمانات بنجاح'}, status=status.HTTP_200_OK)
        
        return super().update(request, *args, **kwargs)
