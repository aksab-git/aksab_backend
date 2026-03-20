from django.db import models, transaction
from django.core.exceptions import ValidationError
# استيراد الموديلات من الملفات الأخرى داخل نفس المجلد (Relative Import)
from .mainInventory import Warehouse, InventoryItem
from .products import Product

class StockTransfer(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'قيد التحضير'),
        ('IN_TRANSIT', 'في الطريق (في عهدة الناقل)'),
        ('COMPLETED', 'تم تأكيد استلام الأمانات (العهد)'),
        ('CANCELLED', 'ملغي'),
    ]

    transfer_no = models.CharField(max_length=50, unique=True, verbose_name="رقم إذن التحويل")
    
    # تصحيح on_delete هنا
    sender_warehouse = models.ForeignKey(Warehouse, related_name='outgoing_transfers', on_delete=models.CASCADE)
    receiver_warehouse = models.ForeignKey(Warehouse, related_name='incoming_transfers', on_delete=models.CASCADE)
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name="الكمية")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            # إنشاء جديد
            super().save(*args, **kwargs)
        else:
            # تحديث حالة موجودة
            old_instance = StockTransfer.objects.get(pk=self.pk)
            
            if old_instance.status == 'COMPLETED':
                raise ValidationError("عفواً، لا يمكن تعديل عهدة تم استلامها وإغلاقها.")

            # تنفيذ العمليات المخزنية داخل Transaction لضمان سلامة البيانات
            with transaction.atomic():
                if old_instance.status == 'PENDING' and self.status == 'IN_TRANSIT':
                    self.process_departure()

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
            raise ValueError(f"الرصيد في {self.sender_warehouse.name} غير كافٍ للتحويل.")
        
        sender_stock.stock_quantity -= self.quantity
        sender_stock.save()

    def process_arrival(self):
        """إضافة الكمية للمخزن المستلم عند تأكيد الاستلام"""
        receiver_stock, created = InventoryItem.objects.select_for_update().get_or_create(
            warehouse=self.receiver_warehouse, 
            product=self.product,
            defaults={'stock_quantity': 0}
        )
        receiver_stock.stock_quantity += self.quantity
        receiver_stock.save()

    class Meta:
        verbose_name = "تحويل عهدة"
        verbose_name_plural = "تحويلات العهد"

    def __str__(self):
        return f"تحويل {self.transfer_no} - {self.product.name}"
