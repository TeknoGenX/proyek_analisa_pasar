from django.db import models

class IndustrialStock(models.Model):
    ticker = models.CharField(max_length=10, help_text="Kode emiten, misal: ASII, UNTR, HEXA")
    date = models.DateField()
    open_price = models.DecimalField(max_digits=15, decimal_places=2)
    high_price = models.DecimalField(max_digits=15, decimal_places=2)
    low_price = models.DecimalField(max_digits=15, decimal_places=2)
    close_price = models.DecimalField(max_digits=15, decimal_places=2)
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ('ticker', 'date')
        ordering = ['-date']

    def __str__(self):
        return f"{self.ticker} - {self.date}"
