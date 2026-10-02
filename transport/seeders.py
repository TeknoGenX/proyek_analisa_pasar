from datetime import timedelta
from .models import TransportStock

def seed_transport_data(today_date):
    tickers = [('BIRD', 1900), ('GIAA', 60), ('ASSA', 780)]
    
    for ticker, base_price in tickers:
        for i in range(5):
            d = today_date - timedelta(days=i)
            TransportStock.objects.get_or_create(
                ticker=ticker, date=d,
                defaults={
                    'open_price': base_price,
                    'high_price': base_price + 30,
                    'low_price': base_price - 20,
                    'close_price': base_price + 10,
                    'volume': 5000000 + i * 400000
                }
            )