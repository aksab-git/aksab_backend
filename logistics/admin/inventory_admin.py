from django.contrib import admin
from ..models.transactions import StockTransfer, TransferItem

# إضافة الأصناف كـ Inline داخل طلب التحويل
class TransferItemInline(admin.TabularInline):
    model = TransferItem
    extra = 0
    fields = ('product', 'quantity', 'unit_at_transfer', 'is_received')

# السطر ده بيحل مشكلة AlreadyRegistered: بيمسح أي تسجيل قديم لو وجد
try:
    admin.site.unregister(StockTransfer)
except admin.sites.NotRegistered:
    pass

@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    # الحقول الحقيقية التي قمنا بتعريفها في الموديل الأخير
    list_display = ('transfer_no', 'requested_by', 'sender_warehouse', 'status', 'created_at')
    list_filter = ('status', 'sender_warehouse', 'created_at')
    search_fields = ('transfer_no', 'requested_by__user__username', 'requested_by__rep_code')
    list_editable = ('status',) # لإتاحة الموافقة السريعة من جدول العرض
    inlines = [TransferItemInline]
    
    # تحسين عرض الأسماء في لوحة التحكم
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('requested_by__user', 'sender_warehouse')

@admin.register(TransferItem)
class TransferItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'transfer', 'quantity', 'is_received')
    list_filter = ('is_received', 'product')
