from datetime import datetime

from zero.screen import read_screen
from zero.importers import read_whatsapp_export, read_text_file, summarize


class FakeBrain:
    def __init__(self):
        self.calls = []

    def chat(self, messages, **kwargs):
        self.calls.append(messages)
        return "özet"


def test_whatsapp_export_parsed(tmp_path):
    p = tmp_path / "chat.txt"
    p.write_text("12.10.2026 14:03 - Ömer: selam\n12.10.2026 14:04 - Ayşe: merhaba\n", encoding="utf-8")
    lines = read_whatsapp_export(p)
    assert lines[0].sender == "Ömer"
    assert lines[0].text == "selam"
    assert isinstance(lines[0].ts, datetime)
    assert lines[1].sender == "Ayşe"


def test_whatsapp_multiline_continuation(tmp_path):
    p = tmp_path / "chat.txt"
    p.write_text("12.10.2026 14:03 - Ömer: ilk satır\ndevam eden satır\n", encoding="utf-8")
    lines = read_whatsapp_export(p)
    assert len(lines) == 1
    assert "devam eden satır" in lines[0].text


def test_read_text_file_encoding(tmp_path):
    p = tmp_path / "mail.txt"
    p.write_text("Türkçe karakterler: şğüöçİ", encoding="utf-8")
    assert "şğüöçİ" in read_text_file(p)


def test_read_screen_uses_injected_ocr():
    out = read_screen(ocr=lambda img: "ekran metni", grab=lambda: "sahte-resim")
    assert out == "ekran metni"


def test_summarize_prompt_turkish():
    brain = FakeBrain()
    summarize(brain, "uzun bir metin içeriği", "kısa özetle")
    blob = " ".join(m["content"] for m in brain.calls[0])
    assert "uzun bir metin içeriği" in blob
    assert "özet" in blob.lower()
