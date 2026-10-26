"""İsteğe bağlı ekran okuma (OCR) — kullanıcı 'ekranımı oku' dediğinde.

WhatsApp'a giriş yapmaz; sadece o anki ekrana bakar → yasak riski yok."""

from __future__ import annotations

_OCR_MISSING = (
    "Ekranı okuyabilmem için yerel OCR motoru (Tesseract) gerekiyor; kurulu "
    "değil gibi. README'deki kuruluma bakabilirsin."
)


def _default_grab():
    import mss
    from PIL import Image

    with mss.mss() as sct:
        shot = sct.grab(sct.monitors[0])
        return Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")


def _default_ocr(image) -> str:
    import pytesseract

    return pytesseract.image_to_string(image, lang="tur")


def read_screen(ocr=None, grab=None) -> str:
    if ocr is not None or grab is not None:
        image = (grab or _default_grab)()
        return (ocr or _default_ocr)(image)
    try:
        image = _default_grab()
        return _default_ocr(image)
    except Exception:
        return _OCR_MISSING
