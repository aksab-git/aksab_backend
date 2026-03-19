from django.contrib import admin
from django.utils.html import format_html
from django import forms
from ..models.mainInventory import Warehouse, InventoryItem
from ..models.products import Product

# --- 1. إدارة المنتجات ---
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'unit', 'selling_price', 'is_active')
    search_fields = ('name', 'sku', 'barcode')
    list_filter = ('unit', 'is_active')

# --- 2. إدارة المخازن (الرئيسي والسيارات) ---
class InventoryInline(admin.TabularInline):
    model = InventoryItem
    extra = 1
    readonly_fields = ('last_updated',)

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'warehouse_type', 'assigned_rep', 'is_active', 'view_inventory_link')
    list_filter = ('warehouse_type', 'is_active')
    search_fields = ('name', 'assigned_rep__user__first_name')
    raw_id_fields = ('assigned_rep',)
    inlines = [InventoryInline] # عرض محتويات المخزن جوه صفحة المخزن نفسه

    def view_inventory_link(self, obj):
        return format_html('<a href="/admin/logistics/inventoryitem/?warehouse__id__exact={}">عرض الجرد 📦</a>', obj.id)
    view_inventory_link.short_description = "محتويات المخزن"

# --- 3. إدارة الجرد (تأمين العهدة) ---
@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'colored_quantity', 'last_updated')
    list_filter = ('warehouse', 'warehouse__warehouse_type', 'product')
    search_fields = ('product__name', 'warehouse__name')
    list_editable = ('stock_quantity',) # للتعديل السريع

    def colored_quantity(self, obj):
        color = 'green' if obj.stock_quantity > 10 else 'red'
        return format_html('<b style="color: {};">{}</b>', color, obj.stock_quantity)
    colored_quantity.short_description = "الكمية الحالية"

# --- 4. منطق التحويل (إضافة "أكشن" للتحويل السريع) ---
# دي هنستخدمها لما نبدأ نعمل StockTransfer، بس حالياً ضفت لك Inlines عشان تسهل عليك الربط

from ..models.transactions import StockTransfer

@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    # عرض البيانات اللوجستية في الجدول الرئيسي
    list_display = ('id', 'sender_warehouse', 'receiver_warehouse', 'product', 'quantity', 'status', 'created_at')
    list_filter = ('status', 'sender_warehouse', 'receiver_warehouse')
    search_fields = ('product__name', 'sender_warehouse__name', 'receiver_warehouse__name')
    
    # تأكيد إن تغيير الحالة للـ Completed هيخصم ويضيف أوتوماتيك
    list_editable = ('status',) 

