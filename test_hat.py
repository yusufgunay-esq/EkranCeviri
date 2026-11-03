"""Uçtan uca hat testi: görüntüye yazı çiz -> OCR -> paragraf -> çeviri."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from ekranceviri import ocr, ceviri
from ekranceviri.paragraf import grupla, renkler

def test_hat():
    im = Image.new("RGB", (700, 220), (30, 30, 40))
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 28)
    d.text((20, 20), "Welcome back, commander.", font=f, fill=(240, 240, 240))
    d.text((20, 60), "Your mission starts in five minutes.", font=f, fill=(240, 240, 240))
    d.text((20, 150), "Settings", font=f, fill=(240, 240, 240))
    rgb = np.array(im)
    ps = grupla(ocr.oku(rgb))
    assert len(ps) == 2, [p.metin for p in ps]
    sonuc = ceviri.cevir_hepsi([p.metin for p in ps])
    assert all(s and s[1] == "en" for s in sonuc), sonuc
    bg, fg = renkler(rgb, ps[0].kutu)
    assert sum(bg) < 200 and sum(fg) > 500, (bg, fg)
    print([s[0] for s in sonuc])

if __name__ == "__main__":
    test_hat()
    print("TAMAM")
