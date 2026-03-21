from django.contrib import admin
from django.contrib.auth.models import User
from .sales_admin import CustomUserAdmin
from ..models.sales_rep import SalesRepresentative
from ..models.sales_manager import SalesManager
from ..models.transactions import StockTransfer, TransferItem # استيراد الموديلات الجديدة

# 1. إعادة تسجيل المستخدمين بصلاحيات مخصصة
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass
admin.site.register(User, CustomUserAdmin)

# 2. تسجيل مندوبي المبيعات والمديرين (تجنب التكرار)
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

# 3. استيراد تسجيلات المخازن والتحويلات من الملفات الفرعية
# السطر ده هينده على inventory_admin اللي إحنا لسه مصلحينه
from .inventory_admin import WarehouseAdmin, InventoryItemAdmin, StockTransferAdmin
