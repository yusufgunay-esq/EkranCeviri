"""OCR, tamamen bilgisayarda. Birincil: Windows'un yerleşik motoru (tam ekran ~0.15 sn).
Yedek: RapidOCR (isteğe bağlı kurulum; Windows motoru metin bulamazsa, CJK vb. için)."""
import asyncio
from dataclasses import dataclass

import numpy as np


@dataclass
class Satir:
    x: int
    y: int
    w: int
    h: int
    metin: str


_win = None
_rapid = None


def _win_motor():
    """Kullanıcı dilleriyle, olmazsa kurulu herhangi bir OCR diliyle motor oluştur."""
    global _win
    if _win is None:
        from winsdk.windows.media.ocr import OcrEngine

        _win = OcrEngine.try_create_from_user_profile_languages()
        if _win is None and OcrEngine.available_recognizer_languages:
            _win = OcrEngine.try_create_from_language(
                OcrEngine.available_recognizer_languages[0])
    return _win


async def _win_oku(rgb: np.ndarray):
    from winsdk.windows.graphics.imaging import BitmapPixelFormat, SoftwareBitmap
    from winsdk.windows.storage.streams import DataWriter

    h, w = rgb.shape[:2]
    bgra = np.dstack([rgb[..., 2], rgb[..., 1], rgb[..., 0], np.full((h, w), 255, np.uint8)])
    yazici = DataWriter()
    yazici.write_bytes(bytearray(bgra.tobytes()))
    bmp = SoftwareBitmap.create_copy_from_buffer(
        yazici.detach_buffer(), BitmapPixelFormat.BGRA8, w, h)
    sonuc = await _win_motor().recognize_async(bmp)
    satirlar = []
    for l in sonuc.lines:
        if not l.words or not l.text.strip():
            continue
        rs = [k.bounding_rect for k in l.words]
        x0 = min(r.x for r in rs)
        y0 = min(r.y for r in rs)
        x1 = max(r.x + r.width for r in rs)
        y1 = max(r.y + r.height for r in rs)
        satirlar.append(Satir(int(x0), int(y0), int(x1 - x0), int(y1 - y0), l.text.strip()))
    return satirlar


def _rapid_oku(rgb):
    global _rapid
    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        return []
    if _rapid is None:
        _rapid = RapidOCR()
    sonuc, _ = _rapid(rgb, use_cls=False)
    satirlar = []
    for kutu, metin, guven in sonuc or []:
        if float(guven) < 0.5 or not metin.strip():
            continue
        xs, ys = [p[0] for p in kutu], [p[1] for p in kutu]
        x, y = int(min(xs)), int(min(ys))
        satirlar.append(Satir(x, y, int(max(xs)) - x, int(max(ys)) - y, metin.strip()))
    return satirlar


def isit():
    try:
        if _win_motor() is not None:
            asyncio.run(_win_oku(np.full((64, 256, 3), 255, np.uint8)))
    except Exception:
        pass


def oku(rgb: np.ndarray):
    satirlar = []
    try:
        if _win_motor() is not None:
            satirlar = asyncio.run(_win_oku(rgb))
    except Exception:
        satirlar = []
    return satirlar or _rapid_oku(rgb)
