from django.contrib import admin
from ..models.mainInventory import Warehouse, InventoryItem

@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    # عرض اسم المخزن، نوعه، المندوب المربوط بيه، وحالته
    list_display = ('name', 'warehouse_type', 'assigned_rep', 'is_active', 'created_at')
    list_filter = ('warehouse_type', 'is_active')
    search_fields = ('name', 'assigned_rep__user__username')
    
    # تحسين شكل اختيار المندوب في لوحة الإدارة
    raw_id_fields = ('assigned_rep',) 

@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    # عرض الصنف والمخزن والكمية
    list_display = ('product', 'warehouse', 'stock_quantity', 'last_updated')
    list_filter = ('warehouse', 'warehouse__warehouse_type')
    search_fields = ('product__name', 'warehouse__name')
    # إمكانية تعديل الكمية مباشرة من الجدول (للجرد السريع)
    list_editable = ('stock_quantity',) 

