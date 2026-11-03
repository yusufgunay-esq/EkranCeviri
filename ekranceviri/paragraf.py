"""Satırları paragraflara birleştirir (bağlam için) ve arka plan/yazı rengini örnekler."""
from dataclasses import dataclass, field

import numpy as np

from .ocr import Satir


@dataclass
class Paragraf:
    satirlar: list = field(default_factory=list)

    @property
    def kutu(self):
        x = min(s.x for s in self.satirlar)
        y = min(s.y for s in self.satirlar)
        r = max(s.x + s.w for s in self.satirlar)
        b = max(s.y + s.h for s in self.satirlar)
        return x, y, r - x, b - y

    @property
    def metin(self):
        return " ".join(s.metin for s in self.satirlar)

    @property
    def satir_yuksekligi(self):
        return sorted(s.h for s in self.satirlar)[len(self.satirlar) // 2]


def _bitisik(p: Paragraf, s: Satir):
    son = p.satirlar[-1]
    h = max(son.h, s.h)
    oran = s.h / max(son.h, 1)
    bosluk = s.y - (son.y + son.h)
    sol_fark = abs(s.x - son.x)
    mrk_fark = abs((s.x + s.w / 2) - (son.x + son.w / 2))
    return (
        0.7 < oran < 1.4
        and -h * 0.3 < bosluk < h * 0.8
        and (sol_fark < h * 1.5 or mrk_fark < h * 1.5)
    )


def grupla(satirlar):
    paragraflar = []
    for s in sorted(satirlar, key=lambda s: (s.y, s.x)):
        for p in paragraflar:
            if _bitisik(p, s):
                p.satirlar.append(s)
                break
        else:
            paragraflar.append(Paragraf([s]))
    return paragraflar


def renkler(rgb: np.ndarray, kutu):
    """(arka_plan, yazı) RGB üçlüleri. Kutunun 3px dış halkasından zemin, içinden zıt renk."""
    x, y, w, h = kutu
    H, W = rgb.shape[:2]
    x0, y0, x1, y1 = max(x - 3, 0), max(y - 3, 0), min(x + w + 3, W), min(y + h + 3, H)
    bolge = rgb[y0:y1, x0:x1].astype(int)
    ic = rgb[max(y, 0):min(y + h, H), max(x, 0):min(x + w, W)].astype(int)
    if bolge.size == 0 or ic.size == 0:
        return (255, 255, 255), (0, 0, 0)
    # zemin: iç bölgede en sık görülen (kuantize) renk
    q = (ic.reshape(-1, 3) // 16)
    anahtar = q[:, 0] * 256 + q[:, 1] * 16 + q[:, 2]
    en_sik = np.bincount(anahtar).argmax()
    maske = anahtar == en_sik
    bg = tuple(int(v) for v in ic.reshape(-1, 3)[maske].mean(axis=0))
    # yazı: zemine en uzak %5 pikselin ortalaması
    uzak = np.abs(ic.reshape(-1, 3) - np.array(bg)).sum(axis=1)
    esik = np.percentile(uzak, 95)
    sec = ic.reshape(-1, 3)[uzak >= esik]
    fg = tuple(int(v) for v in sec.mean(axis=0)) if len(sec) else (0, 0, 0)
    if sum(abs(a - b) for a, b in zip(bg, fg)) < 150:  # kontrast zayıfsa güvenli renk
        lum = 0.299 * bg[0] + 0.587 * bg[1] + 0.114 * bg[2]
        fg = (0, 0, 0) if lum > 128 else (255, 255, 255)
    return bg, fg
