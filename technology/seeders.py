from datetime import timedelta
from .models import TechnologyStock

def seed_technology_data(today_date):
    tickers = [('GOTO', 65), ('BUKA', 120), ('EMTK', 450)]
    
    for ticker, base_price in tickers:
        for i in range(5):
            d = today_date - timedelta(days=i)
            TechnologyStock.objects.get_or_create(
                ticker=ticker, date=d,
                defaults={
                    'open_price': base_price,
                    'high_price': base_price + 3,
                    'low_price': base_price - 2,
                    'close_price': base_price + 1,
                    'volume': 150000000 + i * 20000000
                }
            )