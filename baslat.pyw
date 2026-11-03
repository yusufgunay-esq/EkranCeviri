"""Konsolsuz başlatıcı (pythonw). Çökme olursa %APPDATA%\EkranCeviri\hata.txt'ye yazar."""
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    from ekranceviri.__main__ import main
    main()
except BaseException:
    d = os.path.join(os.environ.get("APPDATA", "."), "EkranCeviri")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "hata.txt"), "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
