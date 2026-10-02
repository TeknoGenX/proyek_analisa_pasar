from datetime import timedelta
from .models import IndustrialStock

def seed_industrial_data(today_date):
    tickers = [('ASII', 5000), ('UNTR', 26000), ('HEXA', 6200)]
    
    for ticker, base_price in tickers:
        for i in range(5):
            d = today_date - timedelta(days=i)
            IndustrialStock.objects.get_or_create(
                ticker=ticker, date=d,
                defaults={
                    'open_price': base_price,
                    'high_price': base_price + 100,
                    'low_price': base_price - 50,
                    'close_price': base_price + 50,
                    'volume': 18000000 + i * 1200000
                }
            )