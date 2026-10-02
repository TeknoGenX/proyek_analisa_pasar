from datetime import timedelta
from .models import PropertyStock

def seed_property_data(today_date):
    tickers = [('BSDE', 1200), ('CTRA', 1300), ('PWON', 460)]
    
    for ticker, base_price in tickers:
        for i in range(5):
            d = today_date - timedelta(days=i)
            PropertyStock.objects.get_or_create(
                ticker=ticker, date=d,
                defaults={
                    'open_price': base_price,
                    'high_price': base_price + 25,
                    'low_price': base_price - 20,
                    'close_price': base_price + 10,
                    'volume': 16000000 + i * 700000
                }
            )