"""Ekranı dondurup üstüne seçim + yerinde çeviri bindiren tam ekran katman."""
import math

import numpy as np
from PySide6.QtCore import QPoint, QRect, QRectF, Qt, QThread, QTimer, Signal
from PySide6.QtGui import (QColor, QCursor, QFont, QFontMetrics, QGuiApplication,
                           QImage, QPainter, QPen)
from PySide6.QtWidgets import QApplication, QWidget

from . import ceviri, ocr
from .paragraf import grupla, renkler

AKSAN = QColor(66, 133, 244)
BAYRAKLAR = Qt.TextWordWrap | Qt.AlignLeft | Qt.AlignTop


def _numpy(img: QImage):
    img = img.convertToFormat(QImage.Format_RGB888)
    w, h, bpl = img.width(), img.height(), img.bytesPerLine()
    arr = np.frombuffer(img.constBits(), np.uint8).reshape(h, bpl)[:, : w * 3]
    return arr.reshape(h, w, 3).copy()


class Is(QThread):
    bitti = Signal(list, str)  # [(kutu, metin, ceviri, bg, fg, satir_h)], hata

    def __init__(self, rgb, hedef):
        super().__init__()
        self.rgb, self.hedef = rgb, hedef

    def run(self):
        try:
            paragraflar = grupla(ocr.oku(self.rgb))
            if not paragraflar:
                self.bitti.emit([], "Metin bulunamadı.")
                return
            sonuc = ceviri.cevir_hepsi([p.metin for p in paragraflar], self.hedef)
            if all(s is None for s in sonuc):
                self.bitti.emit([], "Çeviri için internet bağlantısı gerekiyor.")
                return
            liste = []
            for p, s in zip(paragraflar, sonuc):
                if s is None or s[1] == self.hedef:  # hata ya da zaten hedef dilde
                    continue
                bg, fg = renkler(self.rgb, p.kutu)
                liste.append((p.kutu, p.metin, s[0], bg, fg, p.satir_yuksekligi))
            self.bitti.emit(liste, "" if liste else "Metin zaten Türkçe.")
        except Exception as e:
            self.bitti.emit([], f"Hata: {e}")


class Katman(QWidget):
    def __init__(self, hedef="tr"):
        super().__init__()
        self.hedef = hedef
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.setCursor(Qt.CrossCursor)
        self.setFocusPolicy(Qt.StrongFocus)
        self._zaman = QTimer(self, interval=16)
        self._zaman.timeout.connect(self._tik)
        self._faz = 0.0
        self._is = None
        self._sifirla()

    def _sifirla(self):
        self.durum = "secim"  # secim | calisiyor | bitti
        self.bas = self.son = None
        self.bolge = None
        self.ogeler = []
        self.mesaj = ""
        self.orijinal = False

    # --- giriş ---
    def goster(self):
        if self.isVisible():
            self.kapat()
            return
        ekran = QGuiApplication.screenAt(QCursor.pos()) or QGuiApplication.primaryScreen()
        self.pix = ekran.grabWindow(0)  # tamamı: katman görünmeden önce alınır
        self.dpr = self.pix.devicePixelRatio()
        self._sifirla()
        self.setGeometry(ekran.geometry())
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()
        self.activateWindow()
        self.setFocus()
        self._fade = 0.0
        self._zaman.start()

    def kapat(self):
        self._zaman.stop()
        if self._is and self._is.isRunning():
            self._is.bitti.disconnect()
        self.hide()

    # --- çizim ---
    def _tik(self):
        if self._fade < 1.0:
            self._fade = min(1.0, self._fade + 0.2)
            self.setWindowOpacity(self._fade)
        self._faz = (self._faz + 0.018) % 1.0
        if self.durum == "calisiyor" or self._fade < 1.0:
            self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        p.setRenderHint(QPainter.TextAntialiasing)
        p.drawPixmap(self.rect(), self.pix)

        if self.durum == "bitti":
            self._ciz_sonuc(p)
            return

        # kararma + seçili bölge parlak
        bolge = self._secili()
        koyu = QColor(0, 0, 0, 110)
        if bolge:
            yol = QRectF(self.rect())
            for r in (QRectF(0, 0, self.width(), bolge.top()),
                      QRectF(0, bolge.bottom() + 1, self.width(), self.height()),
                      QRectF(0, bolge.top(), bolge.left(), bolge.height()),
                      QRectF(bolge.right() + 1, bolge.top(), self.width(), bolge.height())):
                p.fillRect(r, koyu)
            p.setPen(QPen(AKSAN, 2))
            p.drawRoundedRect(QRectF(bolge).adjusted(0, 0, -1, -1), 3, 3)
            if self.durum == "calisiyor":
                y = bolge.top() + bolge.height() * (0.5 - 0.5 * math.cos(self._faz * 2 * math.pi))
                p.fillRect(QRectF(bolge.left(), y - 1, bolge.width(), 3),
                           QColor(66, 133, 244, 200))
        else:
            p.fillRect(self.rect(), koyu)
            self._ipucu(p, "Çevirmek için bölgeyi sürükle  ·  Boşluk: tüm ekran  ·  Esc: çık")

    def _ipucu(self, p, metin):
        f = QFont("Segoe UI", 11)
        p.setFont(f)
        r = QFontMetrics(f).boundingRect(metin).adjusted(-16, -9, 16, 9)
        r.moveCenter(QPoint(self.width() // 2, 60))
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(20, 20, 24, 220))
        p.drawRoundedRect(r, r.height() / 2, r.height() / 2)
        p.setPen(QColor(255, 255, 255))
        p.drawText(r, Qt.AlignCenter, metin)

    def _ciz_sonuc(self, p):
        b = self.bolge
        for kutu, metin, tr, bg, fg, satir_h in self.ogeler:
            x, y, w, h = [v / self.dpr for v in kutu]
            x += b.x(); y += b.y()
            metin_ = metin if self.orijinal else tr
            pad = 3
            r = QRect(int(x) - pad, int(y) - pad, int(w) + 2 * pad, int(h) + 2 * pad)
            boyut = max(8, int(satir_h / self.dpr * 0.82))
            alt_sinir = max(8, int(boyut * 0.78))  # çok küçülme, kutu aşağı uzasın
            while True:
                f = QFont("Segoe UI", 10)
                f.setPixelSize(boyut)
                m = QFontMetrics(f)
                gerek = m.boundingRect(QRect(0, 0, r.width(), 10000), BAYRAKLAR, metin_).height()
                if gerek <= r.height() or boyut <= alt_sinir:
                    break
                boyut -= 1
            r.setHeight(max(r.height(), gerek + 2 * pad))
            p.setPen(Qt.NoPen)
            p.setBrush(QColor(*bg))
            p.drawRoundedRect(r, 3, 3)
            p.setFont(f)
            p.setPen(QColor(*fg))
            p.drawText(r.adjusted(pad, pad, -pad, -pad), BAYRAKLAR, metin_)
        if self.mesaj:
            self._ipucu(p, self.mesaj)
        elif self.ogeler:
            self._ipucu(p, "T: orijinal  ·  C: kopyala  ·  Esc/tık: kapat")

    # --- fare / klavye ---
    def _secili(self):
        if self.durum == "calisiyor" or (self.bas and self.son):
            if self.bolge and self.durum != "secim":
                return self.bolge
            return QRect(self.bas, self.son).normalized()
        return None

    def mousePressEvent(self, e):
        if self.durum == "bitti" or e.button() == Qt.RightButton:
            self.kapat()
        elif self.durum == "secim":
            self.bas = self.son = e.position().toPoint()

    def mouseMoveEvent(self, e):
        if self.durum == "secim" and self.bas:
            self.son = e.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, e):
        if self.durum != "secim" or not self.bas:
            return
        r = QRect(self.bas, e.position().toPoint()).normalized()
        if r.width() < 12 or r.height() < 12:
            self.bas = self.son = None
            self.update()
            return
        self._basla(r)

    def keyPressEvent(self, e):
        k = e.key()
        if k == Qt.Key_Escape:
            self.kapat()
        elif k in (Qt.Key_Space, Qt.Key_Return, Qt.Key_Enter) and self.durum == "secim":
            self._basla(QRect(0, 0, self.width(), self.height()))
        elif k == Qt.Key_T and self.durum == "bitti":
            self.orijinal = not self.orijinal
            self.update()
        elif k == Qt.Key_C and self.durum == "bitti" and self.ogeler:
            QApplication.clipboard().setText("\n\n".join(o[2] for o in self.ogeler))
            self.mesaj = "Çeviri panoya kopyalandı"
            self.update()
            QTimer.singleShot(1200, self._mesaj_sil)

    def _mesaj_sil(self):
        self.mesaj = ""
        self.update()

    # --- iş ---
    def _basla(self, r: QRect):
        self.bolge = r
        self.durum = "calisiyor"
        self.setCursor(Qt.BusyCursor)
        fiz = QRect(int(r.x() * self.dpr), int(r.y() * self.dpr),
                    int(r.width() * self.dpr), int(r.height() * self.dpr))
        rgb = _numpy(self.pix.copy(fiz).toImage())
        self._is = Is(rgb, self.hedef)
        self._is.bitti.connect(self._bitti)
        self._is.start()

    def _bitti(self, ogeler, hata):
        self.ogeler, self.mesaj = ogeler, hata
        self.durum = "bitti"
        self.setCursor(Qt.ArrowCursor)
        self.update()
        if hata and not ogeler:
            QTimer.singleShot(1600, self.kapat)
