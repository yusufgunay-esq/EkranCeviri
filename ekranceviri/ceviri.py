"""Çeviri: Google'ın herkese açık ücretsiz ucu, anahtar gerekmez. Paralel + önbellekli."""
import json
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

URL = "https://translate.googleapis.com/translate_a/single"
_pool = ThreadPoolExecutor(max_workers=6)


@lru_cache(maxsize=512)
def _cevir_tek(metin: str, hedef: str):
    """(çeviri, algılanan_dil) döner. Hata olursa istisna fırlatır."""
    params = urllib.parse.urlencode(
        {"client": "gtx", "sl": "auto", "tl": hedef, "dt": "t", "q": metin}
    )
    req = urllib.request.Request(
        f"{URL}?{params}", headers={"User-Agent": "Mozilla/5.0"}
    )
    son = None
    for _ in range(2):
        try:
            with urllib.request.urlopen(req, timeout=8) as r:
                veri = json.loads(r.read().decode("utf-8"))
            ceviri = "".join(parca[0] for parca in veri[0] if parca[0])
            return ceviri, (veri[2] if len(veri) > 2 else "")
        except Exception as e:  # ağ hatası: bir kez daha dene
            son = e
    raise son


def cevir_hepsi(metinler, hedef="tr"):
    """Metin listesini paralel çevirir. Her eleman (çeviri, dil) ya da None (hata)."""
    def is_(m):
        try:
            return _cevir_tek(m, hedef)
        except Exception:
            return None

    return list(_pool.map(is_, metinler))
