from django.db import models

class ForexData(models.Model):
    pair = models.CharField(max_length=10, help_text="Contoh: EURUSD")
    timestamp = models.DateTimeField()
    bid_price = models.DecimalField(max_digits=15, decimal_places=5)
    ask_price = models.DecimalField(max_digits=15, decimal_places=5)
    volume = models.BigIntegerField(default=0)

    class Meta:
        unique_together = ('pair', 'timestamp')
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.pair} - {self.timestamp}"