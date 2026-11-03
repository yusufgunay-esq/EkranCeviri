# Ekran Çeviri

Windows'ta ekrandaki her şeyi tek kısayolla Türkçeye çevirir; Android'deki "Çevir / Circle to Search" gibi.
Çeviri, yazının **kendi yerinde** görünür. API anahtarı, hesap, kayıt gerekmez.

## Kullanım
1. `Ctrl+Shift+E` ekranı dondurur.
2. Bölgeyi sürükle (ya da `Boşluk` ile tüm ekran).
3. Çeviri yerinde belirir. `T` orijinal/çeviri, `C` kopyala, `Esc` veya tık kapatır.

Sistem tepsisinde çalışır; menüden "Windows ile başlat" açılabilir.
Ayarlar: `%APPDATA%\EkranCeviri\ayar.json` (`kisayol`, `hedef` dil kodu).

## Nasıl çalışır
- **OCR:** Windows'un yerleşik motoru, bilgisayarda çalışır (tam ekran ≈ 0,15 sn). İsteğe bağlı RapidOCR yedeği.
- **Çeviri:** Google Translate'in herkese açık ücretsiz ucu; paragraflar paralel çevrilir, sonuçlar önbelleğe alınır.
- Satırlar paragraflara birleştirilir (bağlamlı çeviri); arka plan ve yazı rengi ekrandan örneklenir. Zaten Türkçe metin atlanır.

## Kurulum
    pip install -r requirements.txt
    pyw baslat.pyw      # ya da baslat.vbs (konsolsuz)

Daha iyi İngilizce okuma için (yönetici PowerShell): `Add-WindowsCapability -Online -Name Language.OCR~~~en-US~~~0.0.1.0`

## Test
`python test_hat.py` (OCR → paragraf → çeviri hattı).

## Lisans

Yusuf Günay tarafından geliştirildi. [Mozilla Public License 2.0](LICENSE): başkası kullanabilir ve geliştirebilir; kendi ayrı kodunu kapalı tutabilir, ama bu projenin dosyalarına yaptığı değişiklikler açık kalır ve "Yusuf Günay" telif satırı korunur.
