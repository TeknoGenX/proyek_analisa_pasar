# forex/management/commands/fetch_forex.py
import yfinance as yf
from django.core.management.base import BaseCommand
from django.utils.timezone import make_aware
from forex.models import ForexCandle

class Command(BaseCommand):
    help = 'Mengambil data forex dari Yahoo Finance untuk berbagai timeframe'

    def add_arguments(self, parser):
        parser.add_argument('symbol', type=str, help='Contoh: EURUSD=X atau "all"')
        parser.add_argument('--timeframe', type=str, default='H1', help='Pilihan timeframe: M1, M5, M15, H1, H4, D1, W1')
        parser.add_argument('--period', type=str, default='', help='Rentang data (opsional, misal: 7d, 60d, max)')

    def handle(self, *args, **options):
        symbol_input = options['symbol'].upper()
        tf_input = options['timeframe'].upper()

        # Validasi timeframe yang didukung model
        valid_timeframes = ['M1', 'M5', 'M15', 'H1', 'H4', 'D1', 'W1']
        if tf_input not in valid_timeframes:
            self.stdout.write(self.style.ERROR(f"Timeframe tidak valid! Pilih dari: {', '.join(valid_timeframes)}"))
            return

        # Pemetaan dari Timeframe Django ke parameter Yahoo Finance (interval & default period)
        tf_config = {
            'M1':  {'interval': '1m',  'default_period': '7d'},   # Yahoo batasi 1m maksimal 7 hari
            'M5':  {'interval': '5m',  'default_period': '60d'},  # Yahoo batasi 5m maksimal 60 hari
            'M15': {'interval': '15m', 'default_period': '60d'},  # Yahoo batasi 15m maksimal 60 hari
            'H1':  {'interval': '1h',  'default_period': '730d'}, # Yahoo batasi 1h maksimal 730 hari
            'H4':  {'interval': '1h',  'default_period': '730d'}, # Menggunakan 1h sebagai basis H4
            'D1':  {'interval': '1d',  'default_period': 'max'},
            'W1':  {'interval': '1wk', 'default_period': 'max'},
        }

        conf = tf_config[tf_input]
        interval = conf['interval']
        period = options['period'] if options['period'] else conf['default_period']

        popular_pairs = [
            'EURUSD=X', 'GBPUSD=X', 'USDJPY=X', 'AUDUSD=X', 
            'USDCAD=X', 'NZDUSD=X', 'USDCHF=X', 'USDIDR=X'
        ]

        targets = popular_pairs if symbol_input == 'ALL' else [symbol_input]

        for symbol in targets:
            self.stdout.write(f"Mengambil data {symbol} untuk timeframe {tf_input} (interval: {interval}, period: {period})...")

            try:
                ticker_data = yf.Ticker(symbol)
                df = ticker_data.history(period=period, interval=interval)

                if df.empty:
                    self.stdout.write(self.style.WARNING(f"Tidak ada data ditemukan untuk {symbol}."))
                    continue

                clean_pair = symbol.replace('=X', '')

                count_saved = 0
                for index, row in df.iterrows():
                    dt = index.to_pydatetime()
                    if dt.tzinfo is None:
                        dt = make_aware(dt)

                    ForexCandle.objects.update_or_create(
                        pair=clean_pair,
                        timeframe=tf_input,
                        timestamp=dt,
                        defaults={
                            'open_price': row['Open'],
                            'high_price': row['High'],
                            'low_price': row['Low'],
                            'close_price': row['Close'],
                            'volume': int(row.get('Volume', 0))
                        }
                    )
                    count_saved += 1

                self.stdout.write(self.style.SUCCESS(f'Berhasil menyimpan/memperbarui {count_saved} data candle ({tf_input}) untuk {clean_pair}!'))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Terjadi kesalahan pada {symbol}: {str(e)}"))