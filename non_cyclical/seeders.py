from datetime import timedelta
from .models import NonCyclicalStock

def seed_non_cyclical_data(today_date):
    tickers = [('ICBP', 11500), ('INDF', 6900), ('UNVR', 2300)]
    
    for ticker, base_price in tickers:
        for i in range(5):
            d = today_date - timedelta(days=i)
            NonCyclicalStock.objects.get_or_create(
                ticker=ticker, date=d,
                defaults={
                    'open_price': base_price,
                    'high_price': base_price + 100,
                    'low_price': base_price - 50,
                    'close_price': base_price + 50,
                    'volume': 14000000 + i * 900000
                }
            )