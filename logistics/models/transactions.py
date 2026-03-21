from django.db import models, transaction
from django.utils import timezone
from .mainInventory import Warehouse, InventoryItem
from .products import Product
from .sales_rep import SalesRepresentative

class StockTransfer(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'طلب تحميل (بإنتظار الموافقة)'),
        ('APPROVED', 'تمت الموافقة (قيد التحضير)'),
        ('IN_TRANSIT', 'في الطريق (في عهدة الناقل)'),
        ('COMPLETED', 'تم تأكيد العهدة (استلام كامل)'),
        ('CANCELLED', 'ملغي'),
    ]

    transfer_no = models.CharField(max_length=50, unique=True, verbose_name="رقم الإذن")
    requested_by = models.ForeignKey(SalesRepresentative, on_delete=models.CASCADE, verbose_name="المندوب صاحب الطلب")
    sender_warehouse = models.ForeignKey(Warehouse, related_name='outgoing_transfers', on_delete=models.CASCADE, verbose_name="من مخزن (المصدر)")
    receiver_warehouse = models.ForeignKey(Warehouse, related_name='incoming_transfers', on_delete=models.CASCADE, verbose_name="إلى مخزن (المندوب)")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT', verbose_name="حالة الطلب")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات الطلب")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "إذن تحويل عهدة"
        verbose_name_plural = "أذون تحويل العهد"

    def __str__(self):
        return f"إذن {self.transfer_no} - {self.requested_by.user.username}"

class TransferItem(models.Model):
    transfer = models.ForeignKey(StockTransfer, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="الصنف")
    quantity = models.PositiveIntegerField(verbose_name="الكمية")
    unit_at_transfer = models.CharField(max_length=20, verbose_name="الوحدة وقت الطلب") 
    
    # تأكيد استلام الصنف (الـ Checkbox في الفلاتر)
    is_received = models.BooleanField(default=False, verbose_name="تم تأكيد استلام الصنف")
    received_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity}"

    def save(self, *args, **kwargs):
        # منطق تحديث المخزون عند تأكيد الاستلام (إثبات العهدة)
        if self.pk: # التأكد أن السجل موجود مسبقاً (تحديث وليس إنشاء)
            old_instance = TransferItem.objects.get(pk=self.pk)
            if not old_instance.is_received and self.is_received:
                self.received_at = timezone.now()
                self.process_stock_movement()
        
        super().save(*args, **kwargs)

    def process_stock_movement(self):
        """تخصيص (نقاط أمان) ونقل البضاعة من مخزن المصدر لمخزن المندوب"""
        with transaction.atomic():
            # 1. خصم من مخزن المصدر (مثلاً المخزن الرئيسي)
            sender_item, _ = InventoryItem.objects.get_or_create(
                warehouse=self.transfer.sender_warehouse,
                product=self.product
            )
            sender_item.stock_quantity -= self.quantity
            sender_item.save()

            # 2. إضافة لمخزن المندوب (مخزن السيارة)
            receiver_item, _ = InventoryItem.objects.get_or_create(
                warehouse=self.transfer.receiver_warehouse,
                product=self.product
            )
            receiver_item.stock_quantity += self.quantity
            receiver_item.save()
