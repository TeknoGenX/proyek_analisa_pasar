# forex/seeders.py
from datetime import timedelta
from .models import ForexCandle

def seed_forex_data(current_time):
    """Forex menggunakan parameter current_time untuk perhitungan candle."""
    pairs = [
        ('USDIDR', 15600.0, 15620.0, 15590.0, 15610.0),
        ('EURUSD', 1.0850, 1.0860, 1.0845, 1.0855),
        ('USDJPY', 148.50, 148.70, 148.40, 148.55)
    ]
    
    for pair, open_p, high_p, low_p, close_p in pairs:
        for i in range(5):
            t = current_time - timedelta(hours=i * 4) # Mundur per 4 jam
            ForexCandle.objects.get_or_create(
                pair=pair, 
                timeframe='H4', 
                timestamp=t,
                defaults={
                    'open_price': open_p,
                    'high_price': high_p,
                    'low_price': low_p,
                    'close_price': close_p,
                    'volume': 50000 + i * 5000
                }
            )