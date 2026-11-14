# Ekran Çeviri

by [Yusuf Günay](https://github.com/yusufgunay-esq)

Windows'ta ekrandaki her şeyi tek kısayolla Türkçeye çevirir; Android'deki "Çevir / Circle to Search" gibi.
Çeviri, yazının **kendi yerinde** görünür. API anahtarı, hesap, kayıt gerekmez.

## Özellikler
- **Yerinde Çeviri (Overlay):** Çevrilen metin doğrudan orijinal metnin üzerinde, arka plan ve yazı rengine uyum sağlayarak gösterilir.
- **Hızlı & Yerel OCR:** Windows'un yerleşik OCR altyapısı sayesinde ekrandaki yazılar milisaniyeler içinde yerel olarak çözümlenir.
- **Sıfır Yapılandırma:** API anahtarı, üyelik veya abonelik gerekmez; kurulduğu gibi çalışır.
- **Bağlam Duyarlı:** Satırlar paragraflara akıllıca birleştirilir; Türkçe içerikler otomatik algılanıp filtrelenir.
- **Hızlı Kısayollar:** Tek dokunuşla orijinal/çeviri arasında geçiş (`T`), metni panoya kopyalama (`C`).


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

Yusuf Günay tarafından geliştirildi. [GNU Genel Kamu Lisansı 3.0](LICENSE) (GPLv3 ya da daha sonraki bir sürüm): başkası kullanabilir, geliştirebilir ve dağıtabilir; değiştirip dağıttığı türev çalışma da GPLv3 ile açık kalır. "Yusuf Günay" telif satırı korunur.

GPLv3 bölüm 7(b) uyarınca ek atıf şartı [LICENSE-EK.md](LICENSE-EK.md) dosyasındadır: dağıtımda, Hakkında ekranında ya da eşdeğer yasal bildirimde ve dağıtım sayfasında bağlantıyla birlikte **"Based on Ekran Çeviri by Yusuf Günay"** satırı görünür. Başlığın altındaki "by Yusuf Günay" satırı yazar atfıdır ve korunmalıdır.
