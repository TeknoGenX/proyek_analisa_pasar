import pandas as pd
from django.core.management.base import BaseCommand
from finance.models import FinanceStock

class Command(BaseCommand):
    help = 'Mengimpor histori data saham dari file CSV menggunakan Pandas'

    def add_arguments(self, parser):
        # Argumen wajib: lokasi file CSV
        parser.add_argument('csv_file', type=str, help='Path absolut/relatif ke file CSV')
        
        # Argumen opsional: ticker saham (berguna jika file CSV hanya berisi data 1 emiten tanpa kolom ticker)
        parser.add_argument('--ticker', type=str, help='Nama Ticker (misal: BBCA)', default='UNKNOWN')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        default_ticker = kwargs['ticker']

        try:
            self.stdout.write(self.style.WARNING(f'Membaca file {csv_file}...'))
            
            # 1. Baca CSV menggunakan Pandas
            df = pd.read_csv(csv_file)
            
            # Opsional: Normalisasi nama kolom menjadi huruf kecil agar seragam
            df.columns = [col.strip().lower() for col in df.columns]

            stock_objects = []
            
            # 2. Konversi setiap baris DataFrame menjadi objek Model Django
            for index, row in df.iterrows():
                # Ambil ticker dari CSV, atau gunakan default dari argumen CLI
                current_ticker = row.get('ticker', default_ticker)
                
                stock = FinanceStock(
                    ticker=current_ticker.upper(),
                    date=row['date'],
                    open_price=row['open'],
                    high_price=row['high'],
                    low_price=row['low'],
                    close_price=row['close'],
                    volume=row['volume']
                )
                stock_objects.append(stock)

            # 3. Eksekusi Massal (Bulk Create)
            # ignore_conflicts=True mencegah error jika ada duplikasi data (berdasarkan unique_together date & ticker)
            self.stdout.write(self.style.WARNING('Menyuntikkan data ke database PostgreSQL/SQLite...'))
            FinanceStock.objects.bulk_create(stock_objects, ignore_conflicts=True)
            
            self.stdout.write(self.style.SUCCESS(f'SUKSES! {len(stock_objects)} baris data berhasil diimpor.'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: File {csv_file} tidak ditemukan.'))
        except KeyError as e:
            self.stdout.write(self.style.ERROR(f'Error: Kolom {e} tidak ada di dalam CSV. Pastikan header CSV: date, open, high, low, close, volume.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Gagal mengimpor data: {e}'))