from django.contrib import admin
from .models import Store

@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    # الأعمدة اللي هتظهر في الجدول من بره
    list_display = ('supermarket_name', 'store_type', 'is_active', 'trial_expiry_date')
    # إمكانية البحث باسم المحل
    search_fields = ('supermarket_name',)
    # فلتر جانبي لنوع المحل والحالة
    list_filter = ('store_type', 'is_active')

