"""Katman testi: global tuş yok, widget kendi içinde sürülür, görüntüsü dosyaya alınır."""
import sys
from PySide6.QtCore import QTimer, Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from ekranceviri.overlay import Katman

app = QApplication(sys.argv)
k = Katman("tr")
k.goster()
def sec():
    QTest.keyClick(k, Qt.Key_Space)
def kaydet():
    k.grab().save("_sonuc.png"); print("durum", k.durum, len(k.ogeler), k.mesaj); app.quit()
QTimer.singleShot(800, sec)
QTimer.singleShot(9000, kaydet)
app.exec()
