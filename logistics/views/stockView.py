from rest_framework import viewsets, permissions, status, serializers
from rest_framework.response import Response
from ..models.mainInventory import InventoryItem
from ..models.transactions import StockTransfer, TransferItem
from ..models.products import Product
from ..serializers import InventoryItemSerializer, StockTransferSerializer

# 1. سيريالايزر بسيط للمنتجات (عشان شاشة البحث في الفلاتر)
class ProductListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'unit', 'image', 'base_price']

class AllProductsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    يعرض قائمة بكل المنتجات المتاحة في النظام ليختار منها المندوب أثناء طلب التحميل.
    هذه الـ API هي التي تغذي الـ SearchDelegate في الفلاتر.
    """
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductListSerializer
    permission_classes = [permissions.IsAuthenticated]

class MyInventoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    يعرض للمندوب البضاعة الموجودة في عهدته (سيارته) حالياً.
    """
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        rep_code = self.request.query_params.get('rep_code')

        if rep_code:
            return InventoryItem.objects.filter(
                warehouse__assigned_rep__rep_code=rep_code,
                warehouse__warehouse_type='VAN'
            )

        return InventoryItem.objects.filter(
            warehouse__assigned_rep__user=user,
            warehouse__warehouse_type='VAN'
        )

class MyTransfersViewSet(viewsets.ModelViewSet):
    """
    يعرض "تحويلات العهد" المرسلة للمندوب ليقوم بتأكيد استلامها.
    تسمح للمندوب برؤية الشحنات (العهد المعلقة) التي في الطريق (IN_TRANSIT).
    """
    serializer_class = StockTransferSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        rep_code = self.request.query_params.get('rep_code')

        if rep_code:
            queryset = StockTransfer.objects.filter(
                receiver_warehouse__assigned_rep__rep_code=rep_code
            )
        else:
            queryset = StockTransfer.objects.filter(
                receiver_warehouse__assigned_rep__user=user
            )
        
        return queryset.exclude(status='CANCELLED').order_by('-created_at')

    def update(self, request, *args, **kwargs):
        """
        تأكيد العهدة (الاستلام):
        يتم تحديث الحالة إلى 'COMPLETED' لتشغيل منطق الـ save ونقل الرصيد.
        """
        instance = self.get_object()

        if instance.status != 'IN_TRANSIT':
            return Response(
                {'error': 'عفواً، لا يمكن تأكيد استلام عهدة ليست في الطريق حالياً.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        requested_status = request.data.get('status')
        if requested_status == 'COMPLETED':
            try:
                # تحديث الحالة العامة للإذن
                instance.status = 'COMPLETED'
                instance.save() 

                # تحديث كافة الأصناف داخل الإذن لتصبح "مستلمة" أوتوماتيكياً عند إغلاق الإذن بالكامل
                instance.items.all().update(is_received=True)
                
                return Response({
                    'message': 'تأكيد العهدة: تم استلام الأمانات بنجاح، وتحديث الأرصدة المخزنية.',
                    'transfer_no': instance.transfer_no,
                    'status': instance.status
                }, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(
            {'error': 'غير مسموح بتعديل بيانات العهدة الأصلية. يمكنك فقط تأكيد الاستلام.'}, 
            status=status.HTTP_403_FORBIDDEN
        )
