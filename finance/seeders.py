from datetime import timedelta
import random
from .models import FinanceStock

def seed_finance_data(today_date):
    """Logika kompleks scraping/seeding untuk sektor Finance"""
    tickers = [('BBCA', 10000), ('BBRI', 5100), ('BMRI', 6500)]
    
    for ticker, base_price in tickers:
        for i in range(5):
            d = today_date - timedelta(days=i)
            # Anda bisa menambahkan logika kompleks di sini nantinya (misal baca API sentimen)
            FinanceStock.objects.get_or_create(
                ticker=ticker, date=d,
                defaults={
                    'open_price': base_price,
                    'high_price': base_price + 150,
                    'low_price': base_price - 100,
                    'close_price': base_price + 50,
                    'volume': 35000000 + i * 3000000
                }
            )