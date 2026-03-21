from django.contrib import admin
from django.utils.html import format_html
# استيراد الموديلات - تأكد من مطابقة المسارات لهيكلية مجلداتك
from ..models.product import Product  # إضافة المنتجات
from ..models.mainInventory import Warehouse, InventoryItem
from ..models.transactions import StockTransfer, TransferItem

# --- 1. إدارة المنتجات (التي كانت ناقصة) ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'unit', 'selling_price', 'created_at')
    search_fields = ('name', 'sku')
    list_filter = ('unit',)
    ordering = ('-created_at',)

# --- 2. Inlines لطلبات التحويل (الأصناف داخل الإذن) ---
class TransferItemInline(admin.TabularInline):
    model = TransferItem
    extra = 1 # بيخلي فيه سطر فاضي جاهز للإضافة
    fields = ('product', 'quantity', 'unit_at_transfer', 'is_received')
    autocomplete_fields = ['product'] # بيخليك تبحث في المنتجات بدل القائمة المنسدلة الطويلة

# --- 3. إدارة المخازن ---
@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'warehouse_type', 'assigned_rep', 'is_active')
    list_filter = ('warehouse_type', 'is_active')
    search_fields = ('name',)

# --- 4. إدارة الجرد (Inventory) ---
@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'stock_quantity', 'last_updated')
    list_filter = ('warehouse', 'product')
    search_fields = ('product__name', 'warehouse__name')

# --- 5. إدارة تحويلات العهد (النظام الجديد) ---
# حماية من التكرار عند عمل Reload
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
    readonly_fields = ('transfer_no', 'created_at') # عشان ميتعدلش يدوي بالخطأ
