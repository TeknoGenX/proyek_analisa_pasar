# forex/models.py
from django.db import models

class ForexCandle(models.Model):
    TIMEFRAME_CHOICES = [
        ('M1', '1 Minute'),
        ('M5', '5 Minutes'),
        ('M15', '15 Minutes'),
        ('H1', '1 Hour'),
        ('H4', '4 Hours'),
        ('D1', '1 Day'),
        ('W1', '1 Week'),
    ]

    pair = models.CharField(max_length=10, db_index=True, help_text="Contoh: EURUSD")
    timeframe = models.CharField(max_length=5, choices=TIMEFRAME_CHOICES, default='H1')
    timestamp = models.DateTimeField()
    
    # OHLC (Open, High, Low, Close)
    open_price = models.DecimalField(max_digits=15, decimal_places=5)
    high_price = models.DecimalField(max_digits=15, decimal_places=5)
    low_price = models.DecimalField(max_digits=15, decimal_places=5)
    close_price = models.DecimalField(max_digits=15, decimal_places=5)
    
    volume = models.BigIntegerField(default=0)

    class Meta:
        unique_together = ('pair', 'timeframe', 'timestamp')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['pair', 'timeframe', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.pair} ({self.timeframe}) - {self.timestamp}: {self.close_price}"