from django.contrib import admin
from ..models.transactions import StockTransfer, TransferItem  # تأكد من الاسم TransferItem

class TransferItemInline(admin.TabularInline):
    model = TransferItem
    extra = 0

@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    # الحقول الحقيقية الموجودة في الموديل الجديد
    list_display = ('transfer_no', 'requested_by', 'sender_warehouse', 'status', 'created_at')
    list_filter = ('status', 'sender_warehouse')
    search_fields = ('transfer_no', 'requested_by__user__username')
    inlines = [TransferItemInline]
from django.contrib import admin
from ..models.transactions import StockTransfer, TransferItem  # تأكد من الاسم TransferItem

class TransferItemInline(admin.TabularInline):
    model = TransferItem
    extra = 0

@admin.register(StockTransfer)
class StockTransferAdmin(admin.ModelAdmin):
    # الحقول الحقيقية الموجودة في الموديل الجديد
    list_display = ('transfer_no', 'requested_by', 'sender_warehouse', 'status', 'created_at')
    list_filter = ('status', 'sender_warehouse')
    search_fields = ('transfer_no', 'requested_by__user__username')
    inlines = [TransferItemInline]
