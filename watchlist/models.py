from django.db import models
from django.contrib.auth.models import User

class WatchlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=64, blank=True, null=True)
    ticker = models.CharField(max_length=10)
    sector = models.CharField(max_length=50, default='General')
    target_price = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.ticker} ({self.sector})"
