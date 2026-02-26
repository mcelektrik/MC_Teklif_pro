# MC_Teklif_Pro

MC_Teklif_Pro, Windows için geliştirilmiş, offline çalışabilen, teklif hazırlama ve PDF üretme uygulamasıdır.

## Özellikler
- **Teklif Hazırlama:** Müşteri bilgileri, kalemler, fiyatlar, KDV ve iskonto hesaplamaları.
- **PDF Üretimi:** Profesyonel görünümlü PDF çıktıları (HTML/CSS tabanlı).
- **Offline Çalışma:** İnternet bağlantısı gerektirmez.
- **Otomatik Kayıt:** Çalışmalarınız otomatik olarak taslak olarak kaydedilir.
- **Arşivleme:** Teklifleriniz SQLite veritabanında saklanır ve düzenli yedeklenir.

## Kurulum
1. `MC_Teklif_Pro_Setup.exe` dosyasını çalıştırın.
2. Kurulum sihirbazını takip edin.
3. Masaüstündeki kısayoldan uygulamayı başlatın.

## Geliştirme Ortamı Kurulumu
Bu projeyi geliştirmek veya kaynak kodundan çalıştırmak için:

1. Python 3.12+ kurulu olduğundan emin olun.
2. PowerShell'i yönetici olarak çalıştırın (gerekirse).
3. Proje dizininde şu komutu çalıştırın:
   ```powershell
   .\scripts\setup.ps1
   ```
   Bu komut sanal ortamı oluşturur, bağımlılıkları yükler ve testleri çalıştırır.

## Build (Exe Oluşturma)
Dağıtılabilir `Setup.exe` dosyasını oluşturmak için:
1. Inno Setup 6'nın kurulu olduğundan emin olun.
2. Şu komutu çalıştırın:
   ```powershell
   .\scripts\build.ps1
   ```
   Çıktı `dist_installer` klasöründe olacaktır.

## Lisans
Bu proje özel mülkiyettir.
