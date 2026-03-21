from django.db import models, transaction
from django.core.exceptions import ValidationError
from .mainInventory import Warehouse, InventoryItem
from .products import Product

class StockTransfer(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'طلب تحميل (بإنتظار الموافقة)'), # للمندوب
        ('PENDING', 'قيد التحضير (بإنتظار المخزن)'), # للإدارة
        ('IN_TRANSIT', 'في الطريق (في عهدة الناقل)'), 
        ('COMPLETED', 'تمت التسوية (استلام كامل)'),
        ('PARTIAL', 'استلام جزئي'),
        ('CANCELLED', 'ملغي'),
    ]

    transfer_no = models.CharField(max_length=50, unique=True, verbose_name="رقم الإذن")
    sender_warehouse = models.ForeignKey(Warehouse, related_name='outgoing_transfers', on_delete=models.CASCADE)
    receiver_warehouse = models.ForeignKey(Warehouse, related_name='incoming_transfers', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "إذن تحويل عهدة"
        verbose_name_plural = "أذون تحويل العهد"

    def __str__(self):
        return f"إذن {self.transfer_no} - {self.get_status_display()}"

class TransferItem(models.Model):
    transfer = models.ForeignKey(StockTransfer, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name="الكمية المطلوبة")
    is_confirmed = models.BooleanField(default=False, verbose_name="تم الاستلام؟") # ده للـ Checkbox
    confirmed_at = models.DateTimeField(null=True, blank=True)

    def confirm_item(self):
        """الـ Logic اللي بينقل الصنف للمخزن لما المندوب يعمل Check"""
        if not self.is_confirmed:
            with transaction.atomic():
                # 1. تأكيد الصنف
                self.is_confirmed = True
                self.confirmed_at = models.DateTimeField(auto_now=True)
                
                # 2. تحديث مخزن المندوب (زيادة)
                receiver_stock, _ = InventoryItem.objects.get_or_create(
                    warehouse=self.transfer.receiver_warehouse,
                    product=self.product,
                    defaults={'stock_quantity': 0}
                )
                receiver_stock.stock_quantity += self.quantity
                receiver_stock.save()
                
                self.save()
