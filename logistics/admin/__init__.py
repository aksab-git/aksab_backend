from django.contrib import admin
from django.contrib.auth.models import User
from .sales_admin import CustomUserAdmin
from ..models.sales_rep import SalesRepresentative
from ..models.sales_manager import SalesManager

# استيراد كلاسات الـ Admin من الملفات الفرعية
# تأكد إن الأسماء هنا مطابقة تماماً للي فوق
from .inventory_admin import WarehouseAdmin, InventoryItemAdmin, StockTransferAdmin

# 1. تنظيف وتسجيل مستخدمين النظام
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)

# 2. تسجيل مندوبي المبيعات والمديرين
try:
    admin.site.unregister(SalesRepresentative)
except admin.sites.NotRegistered:
    pass
admin.site.register(SalesRepresentative)

try:
    admin.site.unregister(SalesManager)
except admin.sites.NotRegistered:
    pass
admin.site.register(SalesManager)

# ملاحظة: تم تسجيل Warehouse, InventoryItem, و StockTransfer 
# داخل ملف inventory_admin.py باستخدام الـ Decorator @admin.register
