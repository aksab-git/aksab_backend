from django.db import models, transaction
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
    sender_warehouse = models.ForeignKey(Warehouse, related_name='outgoing_transfers', on_delete=models.CASCADE, verbose_name="من مخزن")
    receiver_warehouse = models.ForeignKey(Warehouse, related_name='incoming_transfers', on_delete=models.CASCADE, verbose_name="إلى مخزن")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="الصنف")
    quantity = models.PositiveIntegerField(verbose_name="الكمية المحولة")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="حالة العهدة")
    
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات التحميل")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # منطق الربط الأوتوماتيكي: تنفيذ الخصم والإضافة فقط عند حالة "تم الاستلام"
        if self.status == 'COMPLETED':
            with transaction.atomic():
                # 1. الخصم من المخزن المرسل (تأمين العهدة)
                sender_stock, _ = InventoryItem.objects.get_or_create(
                    warehouse=self.sender_warehouse, 
                    product=self.product
                )
                if sender_stock.stock_quantity >= self.quantity:
                    sender_stock.stock_quantity -= self.quantity
                    sender_stock.save()
                    
                    # 2. الإضافة لمخزن المستقبل (تأكيد العهدة)
                    receiver_stock, _ = InventoryItem.objects.get_or_create(
                        warehouse=self.receiver_warehouse, 
                        product=self.product
                    )
                    receiver_stock.stock_quantity += self.quantity
                    receiver_stock.save()
                else:
                    raise ValueError(f"عفواً! الرصيد في {self.sender_warehouse.name} لا يكفي.")
        
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "تحويل عهدة"
        verbose_name_plural = "تحويلات العهد (المخزنية)"

