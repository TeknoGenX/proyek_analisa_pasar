from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date

# Import fungsi seeder/scraper dari 12 app sesuai struktur proyek
from basic_idn.seeders import seed_basic_industry_data
from cyclical.seeders import seed_cyclical_data
from energy.seeders import seed_energy_data
from finance.seeders import seed_finance_data
from health.seeders import seed_health_data
from industrial.seeders import seed_industrial_data
from infrastructure.seeders import seed_infrastructure_data
from non_cyclical.seeders import seed_non_cyclical_data
from property.seeders import seed_property_data
from technology.seeders import seed_technology_data
from transport.seeders import seed_transport_data
from forex.seeders import seed_forex_data

class Command(BaseCommand):
    help = 'Orkestrasi eksekusi scraping dan seeding data pasar secara terisolasi untuk 12 sektor'

    def handle(self, *args, **options):
        today = date.today()
        now = timezone.now()

        self.stdout.write(self.style.WARNING("=== Memulai orkestrasi scraping per sektor ===\n"))

        # Mendaftarkan seluruh sektor ke dalam list eksekusi (Task Runner)
        # Format: (Nama Tampilan, Fungsi Seeder, Parameter Waktu)
        seeding_tasks = [
            ("Basic Industry", seed_basic_industry_data, today),
            ("Cyclical", seed_cyclical_data, today),
            ("Energy", seed_energy_data, today),
            ("Finance", seed_finance_data, today),
            ("Health", seed_health_data, today),
            ("Industrial", seed_industrial_data, today),
            ("Infrastructure", seed_infrastructure_data, today),
            ("Non-Cyclical", seed_non_cyclical_data, today),
            ("Property", seed_property_data, today),
            ("Technology", seed_technology_data, today),
            ("Transport", seed_transport_data, today),
            ("Forex", seed_forex_data, now), # Forex ditarik terakhir menggunakan timestamp intra-day
        ]

        success_count = 0
        error_count = 0

        # Eksekusi secara terisolasi (Fault-Tolerant)
        for sector_name, seeder_func, time_param in seeding_tasks:
            self.stdout.write(f"Menarik data {sector_name}...")
            try:
                # Menjalankan fungsi spesifik dari masing-masing app
                seeder_func(time_param)
                self.stdout.write(self.style.SUCCESS(f"  [OK] Data {sector_name} berhasil disimpan."))
                success_count += 1
            except Exception as e:
                # Jika scraping satu sektor gagal, catat error dan lanjut ke sektor berikutnya
                self.stdout.write(self.style.ERROR(f"  [GAGAL] Error pada {sector_name}: {str(e)}"))
                error_count += 1

        # Laporan Hasil Eksekusi
        self.stdout.write(self.style.WARNING("\n=== Ringkasan Scraping & Seeding ==="))
        self.stdout.write(f"Berhasil: {success_count} sektor")
        self.stdout.write(f"Gagal   : {error_count} sektor")

        if error_count == 0:
            self.stdout.write(self.style.SUCCESS('\nSemua logic scraping & seeding berhasil tereksekusi tanpa error!'))
        else:
            self.stdout.write(self.style.NOTICE('\nProses selesai, namun terdapat beberapa error. Silakan periksa log di atas untuk melakukan debug pada scraper yang bermasalah.'))