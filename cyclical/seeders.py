from datetime import timedelta
from .models import CyclicalStock

def seed_cyclical_data(today_date):
    tickers = [('ACES', 850), ('MAPI', 1600), ('ERAA', 420)]
    
    for ticker, base_price in tickers:
        for i in range(5):
            d = today_date - timedelta(days=i)
            CyclicalStock.objects.get_or_create(
                ticker=ticker, date=d,
                defaults={
                    'open_price': base_price,
                    'high_price': base_price + 20,
                    'low_price': base_price - 15,
                    'close_price': base_price + 10,
                    'volume': 8000000 + i * 500000
                }
            )