# Ekran Çeviri

[![Lisans: MPL-2.0](https://img.shields.io/badge/lisans-MPL--2.0-4c90f0?style=flat-square)](LICENSE)
![Platform: Windows 10/11](https://img.shields.io/badge/platform-Windows%2010%20%7C%2011-1e242c?style=flat-square)
![Python](https://img.shields.io/badge/Python-3-1e242c?style=flat-square)
![API anahtarı gerekmez](https://img.shields.io/badge/API%20anahtar%C4%B1-gerekmez-2ea043?style=flat-square)

**Windows ekran çevirici · OCR ile yerinde çeviri · Screen translator for Windows** · [English ↓](#english)

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

Yusuf Günay tarafından geliştirildi. [Mozilla Public License 2.0](LICENSE): başkası kullanabilir ve geliştirebilir; kendi ayrı kodunu kapalı tutabilir, ama bu projenin dosyalarına yaptığı değişiklikler açık kalır ve "Yusuf Günay" telif satırı korunur.

---

## English

**Ekran Çeviri** is a free, open-source **screen translator for Windows**: press one hotkey, drag over any part of the screen, and the translation appears **in place, right on top of the original text** — like "Circle to Search / Translate" on Android, but for the Windows desktop. No API key, no account, no sign-up.

- **In-place overlay translation** that samples the background and text color so it blends in.
- **Fast local OCR** via the built-in Windows OCR engine (full screen ≈ 0.15 s), with an optional RapidOCR fallback for CJK scripts.
- **Context-aware:** lines are merged into paragraphs before translating; text already in the target language is skipped.
- **Hotkeys:** `Ctrl+Shift+E` freeze & select, `Space` whole screen, `T` toggle original/translation, `C` copy, `Esc` close.
- Runs from the system tray; target language is configurable (`hedef` in `%APPDATA%\EkranCeviri\ayar.json`), default Turkish.

Use it to read games, videos, apps, images and PDFs in a foreign language without copy-pasting.

```
pip install -r requirements.txt
pyw baslat.pyw
```

Built with Python, PySide6 and the Windows Runtime OCR API. Licensed under MPL-2.0.
