import json
import os
import sys
import threading
from pathlib import Path

from PySide6.QtCore import QLockFile, QDir
from PySide6.QtGui import QAction, QColor, QFont, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from . import ocr
from .kisayol import Kisayol
from .overlay import Katman

AYAR = Path(os.environ.get("APPDATA", Path.home())) / "EkranCeviri" / "ayar.json"
VARSAYILAN = {"kisayol": "ctrl+shift+e", "hedef": "tr"}
BASLANGIC = (Path(os.environ.get("APPDATA", "")) / "Microsoft/Windows/Start Menu/Programs/Startup"
             / "EkranCeviri.vbs")


def ayar_oku():
    try:
        return {**VARSAYILAN, **json.loads(AYAR.read_text(encoding="utf-8"))}
    except Exception:
        AYAR.parent.mkdir(parents=True, exist_ok=True)
        AYAR.write_text(json.dumps(VARSAYILAN, indent=2), encoding="utf-8")
        return dict(VARSAYILAN)


def simge():
    pm = QPixmap(64, 64)
    pm.fill(QColor(0, 0, 0, 0))
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setBrush(QColor(66, 133, 244))
    p.setPen(QColor(0, 0, 0, 0))
    p.drawRoundedRect(4, 4, 56, 56, 14, 14)
    p.setPen(QColor(255, 255, 255))
    p.setFont(QFont("Segoe UI", 28, QFont.Bold))
    p.drawText(pm.rect(), 0x84, "çA")
    p.end()
    return QIcon(pm)


def baslangic_acik():
    return BASLANGIC.exists()


def baslangic_ayarla(ac):
    if ac:
        pyw = Path(sys.executable).with_name("pythonw.exe")
        kok = Path(__file__).resolve().parent.parent
        BASLANGIC.write_text(
            'Set s = CreateObject("WScript.Shell")\n'
            f's.CurrentDirectory = "{kok}"\n'
            f's.Run """{pyw}"" -m ekranceviri", 0, False\n', encoding="utf-8")
    elif BASLANGIC.exists():
        BASLANGIC.unlink()


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    kilit = QLockFile(QDir.temp().filePath("ekranceviri.lock"))
    if not kilit.tryLock(100):
        return  # zaten çalışıyor
    ayar = ayar_oku()
    katman = Katman(ayar["hedef"])
    threading.Thread(target=ocr.isit, daemon=True).start()  # OCR'ı önceden ısıt

    kisayol = Kisayol(ayar["kisayol"])
    kisayol.basildi.connect(katman.goster)

    tray = QSystemTrayIcon(simge(), app)
    menu = QMenu()
    a = QAction(f"Çevir ({ayar['kisayol'].upper()})", menu)
    a.triggered.connect(katman.goster)
    menu.addAction(a)
    b = QAction("Windows ile başlat", menu, checkable=True, checked=baslangic_acik())
    b.toggled.connect(baslangic_ayarla)
    menu.addAction(b)
    menu.addSeparator()
    c = QAction("Çıkış", menu)
    c.triggered.connect(lambda: (kisayol.durdur(), app.quit()))
    menu.addAction(c)
    tray.setContextMenu(menu)
    tray.setToolTip("Ekran Çeviri")
    tray.show()
    if kisayol.hata:
        tray.showMessage("Ekran Çeviri", kisayol.hata, QSystemTrayIcon.Warning, 6000)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
