"""Win32 RegisterHotKey ile küresel kısayol (düşük seviye klavye kancası yok, hafif)."""
import ctypes
import threading
from ctypes import wintypes

from PySide6.QtCore import QObject, Signal

MOD = {"alt": 1, "ctrl": 2, "shift": 4, "win": 8}
WM_HOTKEY = 0x0312
_NOREPEAT = 0x4000


def _coz(kisayol: str):
    modlar, tus = 0, None
    for parca in kisayol.lower().replace(" ", "").split("+"):
        if parca in MOD:
            modlar |= MOD[parca]
        elif len(parca) == 1:
            tus = ord(parca.upper())
        elif parca.startswith("f") and parca[1:].isdigit():
            tus = 0x70 + int(parca[1:]) - 1
        else:
            raise ValueError(f"Bilinmeyen tuş: {parca}")
    if tus is None:
        raise ValueError("Kısayolda tuş yok")
    return modlar, tus


class Kisayol(QObject):
    basildi = Signal()

    def __init__(self, kisayol: str):
        super().__init__()
        self._modlar, self._tus = _coz(kisayol)
        self._tid = None
        self.hata = None
        self._hazir = threading.Event()
        threading.Thread(target=self._dongu, daemon=True).start()
        self._hazir.wait(2)

    def _dongu(self):
        u32 = ctypes.windll.user32
        self._tid = ctypes.windll.kernel32.GetCurrentThreadId()
        if not u32.RegisterHotKey(None, 1, self._modlar | _NOREPEAT, self._tus):
            self.hata = "Kısayol başka bir program tarafından kullanılıyor."
            self._hazir.set()
            return
        self._hazir.set()
        msg = wintypes.MSG()
        while u32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            if msg.message == WM_HOTKEY:
                self.basildi.emit()
        u32.UnregisterHotKey(None, 1)

    def durdur(self):
        if self._tid:
            ctypes.windll.user32.PostThreadMessageW(self._tid, 0x0012, 0, 0)  # WM_QUIT
