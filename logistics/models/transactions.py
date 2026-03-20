from django.db import models, transaction
from django.core.exceptions import ValidationError

class StockTransfer(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'قيد التحضير'),
        ('IN_TRANSIT', 'في الطريق (في عهدة الناقل)'),
        ('COMPLETED', 'تم تأكيد استلام الأمانات (العهد)'),
        ('CANCELLED', 'ملغي'),
    ]

    transfer_no = models.CharField(max_length=50, unique=True, verbose_name="رقم إذن التحويل")
    sender_warehouse = models.ForeignKey('Warehouse', related_name='outgoing_transfers', on_get=models.CASCADE)
    receiver_warehouse = models.ForeignKey('Warehouse', related_name='incoming_transfers', on_get=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name="الكمية")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            # عند إنشاء التحويل أول مرة
            super().save(*args, **kwargs)
        else:
            old_instance = StockTransfer.objects.get(pk=self.pk)
            
            # منع التعديل بعد الاكتمال
            if old_instance.status == 'COMPLETED':
                raise ValidationError("عفواً، لا يمكن تعديل عهدة تم استلامها وإغلاقها.")

            with transaction.atomic():
                # الحالة 1: من PENDING إلى IN_TRANSIT (خروج من المخزن لعهدة الطريق)
                if old_instance.status == 'PENDING' and self.status == 'IN_TRANSIT':
                    self.process_departure()

                # الحالة 2: من IN_TRANSIT إلى COMPLETED (تأكيد الاستلام النهائي)
                elif old_instance.status == 'IN_TRANSIT' and self.status == 'COMPLETED':
                    self.process_arrival()

            super().save(*args, **kwargs)

    def process_departure(self):
        """خصم الكمية من المخزن المرسل عند خروجها للطريق"""
        sender_stock = InventoryItem.objects.select_for_update().get(
            warehouse=self.sender_warehouse, 
            product=self.product
        )
        if sender_stock.stock_quantity < self.quantity:
            raise ValueError(f"الرصيد في {self.sender_warehouse.name} غير كافٍ.")
        
        sender_stock.stock_quantity -= self.quantity
        sender_stock.save()

    def process_arrival(self):
        """إضافة الكمية للمخزن المستلم عند تأكيد الاستلام"""
        receiver_stock, _ = InventoryItem.objects.select_for_update().get_or_create(
            warehouse=self.receiver_warehouse, 
            product=self.product,
            defaults={'stock_quantity': 0}
        )
        receiver_stock.stock_quantity += self.quantity
        receiver_stock.save()

    class Meta:
        verbose_name = "تحويل عهدة"
        verbose_name_plural = "تحويلات العهد"
