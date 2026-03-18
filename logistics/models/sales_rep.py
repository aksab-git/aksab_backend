from django.db import models
from django.contrib.auth.models import User

class SalesRepresentative(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='sales_rep_profile')
    address = models.CharField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, unique=True)
    rep_code = models.CharField(max_length=50, unique=True, editable=False) # غير قابل للتعديل يدوي
    targets = models.JSONField(default=dict, blank=True)
    insurance_points = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    supervisor = models.ForeignKey('SalesManager', on_delete=models.SET_NULL, null=True, blank=True, related_name='reps')

    def save(self, *args, **kwargs):
        if not self.rep_code:
            # توليد كود تلقائي بناءً على رقم التليفون أو الـ ID
            self.rep_code = f"REP-{self.phone[-4:]}" # مثال: REP + آخر 4 أرقام
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.rep_code})"
