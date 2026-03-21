from django.contrib import admin
from django.utils.html import format_html
from ..models.mainInventory import Warehouse, InventoryItem
from ..models.transactions import StockTransfer, TransferItem

# --- 1. Inlines لطلبات التحويل ---
class TransferItemInline(admin.TabularInline):
    model = TransferItem
    extra = 0
    fields = ('product', 'quantity', 'unit_at_transfer', 'is_received')

# --- 2. إدارة المخازن ---
@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    list_display = ('name', 'warehouse_type', 'assigned_rep', 'is_active')
    list_filter = ('warehouse_type', 'is_active')
    search_fields = ('name',)

# --- 3. إدارة الجرد ---
@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('product', 'warehouse', 'stock_quantity', 'last_updated')
    list_filter = ('warehouse', 'product')
    search_fields = ('product__name', 'warehouse__name')

# --- 4. إدارة تحويلات العهد (النظام الجديد) ---
# حماية من التكرار
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
