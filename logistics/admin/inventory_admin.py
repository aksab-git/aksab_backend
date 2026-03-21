from django.contrib import admin
from django.utils.html import format_html

# استيراد الموديلات باستخدام المسار المباشر لتجنب أخطاء السيرفر
from logistics.models.product import Product
from logistics.models.mainInventory import Warehouse, InventoryItem
from logistics.models.transactions import StockTransfer, TransferItem

# --- 1. إدارة المنتجات ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'unit', 'selling_price')
    search_fields = ('name', 'sku')
    list_filter = ('unit',)

# --- 2. الأصناف داخل إذن التحويل (Inline) ---
class TransferItemInline(admin.TabularInline):
    model = TransferItem
    extra = 1
    fields = ('product', 'quantity', 'unit_at_transfer', 'is_received')
    # تأكد من أن الموديل يحتوي على ForeignKey لـ Product
    autocomplete_fields = ['product'] 

# --- 3. إدارة المخازن ---
@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'warehouse_type', 'assigned_rep', 'is_active')
    list_filter = ('warehouse_type', 'is_active')
    search_fields = ('name',)

# --- 4. إدارة الجرد ---
@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'stock_quantity', 'last_updated')
    list_filter = ('warehouse', 'product')
    search_fields = ('product__name', 'warehouse__name')

# --- 5. إدارة أذون تحويل العهد ---
# مسح التسجيل القديم لو موجود لتفادي التعارض
try:
    admin.site.unregister(StockTransfer)
except admin.sites.NotRegistered:
    pass

@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    list_display = ('transfer_no', 'requested_by', 'sender_warehouse', 'status', 'created_at')
    list_filter = ('status', 'sender_warehouse', 'created_at')
    search_fields = ('transfer_no', 'requested_by__user__username')
    list_editable = ('status',)
    inlines = [TransferItemInline]
