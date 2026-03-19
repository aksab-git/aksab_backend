from rest_framework import viewsets, permissions
from ..models.mainInventory import InventoryItem
from ..models.transactions import StockTransfer
from ..serializers import InventoryItemSerializer, StockTransferSerializer

class MyInventoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    يعرض للمندوب البضاعة الموجودة في عهدته (سيارته) حالياً
    """
    serializer_class = InventoryItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # تصفية البضاعة لتظهر فقط ما يخص المندوب المسجل دخوله
        return InventoryItem.objects.filter(warehouse__assigned_rep__user=self.request.user)

class MyTransfersViewSet(viewsets.ModelViewSet):
    """
    يعرض "تحويلات العهد" المرسلة للمندوب ليقوم بتأكيد استلامها
    """
    serializer_class = StockTransferSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # تصفية التحويلات لتظهر فقط ما هو مرسل لمخزن هذا المندوب
        return StockTransfer.objects.filter(receiver_warehouse__assigned_rep__user=self.request.user)

