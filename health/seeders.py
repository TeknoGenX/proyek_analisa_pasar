from datetime import timedelta
from .models import HealthStock

def seed_health_data(today_date):
    tickers = [('KLBF', 1650), ('MIKA', 2800), ('SIDO', 680)]
    
    for ticker, base_price in tickers:
        for i in range(5):
            d = today_date - timedelta(days=i)
            HealthStock.objects.get_or_create(
                ticker=ticker, date=d,
                defaults={
                    'open_price': base_price,
                    'high_price': base_price + 30,
                    'low_price': base_price - 20,
                    'close_price': base_price + 10,
                    'volume': 12000000 + i * 800000
                }
            )