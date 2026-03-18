from django.db import models
from django.contrib.auth.models import User

class SalesManager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sales_manager_profile')
    role = models.CharField(max_length=30, choices=[('sales_supervisor', 'مشرف'), ('sales_manager', 'مدير')])
    phone = models.CharField(max_length=20, unique=True)
    geographic_area = models.JSONField(default=list, blank=True)

    def __str__(self):
        return f"{self.role}: {self.user.username}"
