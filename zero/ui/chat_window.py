"""HUD sohbet penceresi + test edilebilir görünüm modeli.

ChatViewModel PySide6'ya bağlı DEĞİLDİR (bu yüzden test edilebilir). PySide6 yalnızca
gerçek pencere kurulurken (build_chat_window) tembel içe aktarılır."""

from __future__ import annotations


class ChatViewModel:
    def __init__(self, app, profile: str):
        self.app = app
        self.profile = profile

    def send(self, text: str) -> str:
        return self.app.chat_turn(self.profile, text)

    def send_stream(self, text: str, on_chunk) -> str:
        return self.app.chat_turn_stream(self.profile, text, on_chunk)

    def history(self):
        return self.app.store.all_messages(self.profile)


def build_chat_window(view_model: ChatViewModel):  # pragma: no cover - GUI
    """Köşede yaşayan, koyu temalı HUD sohbet penceresi döndürür."""
    from pathlib import Path

    import threading

    from PySide6.QtCore import Qt, QObject, Signal
    from PySide6.QtWidgets import (
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QTextEdit,
        QLineEdit,
        QPushButton,
        QLabel,
    )

    win = QWidget()
    win.setWindowTitle("ZeRo")
    # Normal başlık çubuğu: taşınabilir + kapatma düğmesi olsun (üstte takılı kalmasın).
    win.setWindowFlags(Qt.Window)
    win.resize(380, 520)

    layout = QVBoxLayout(win)
    header = QLabel("ZeRo")
    header.setObjectName("zeroHeader")
    layout.addWidget(header)

    transcript = QTextEdit()
    transcript.setReadOnly(True)
    transcript.setObjectName("zeroTranscript")
    layout.addWidget(transcript)

    row = QHBoxLayout()
    entry = QLineEdit()
    entry.setPlaceholderText("ZeRo'ya yaz…")
    send_btn = QPushButton("Gönder")
    row.addWidget(entry)
    row.addWidget(send_btn)
    layout.addLayout(row)

    for m in view_model.history():
        who = "Sen" if m.role == "user" else "ZeRo"
        transcript.append(f"<b>{who}:</b> {m.text}")

    # Cevap arka plan thread'inde üretilir ve kelime kelime akar; sinyallerle
    # ana thread'e taşınır (pencere donmaz, cevap anında yazmaya başlar).
    from PySide6.QtGui import QTextCursor

    class _Bridge(QObject):
        chunk = Signal(str)
        done = Signal()

    bridge = _Bridge()

    def _append_delta(delta: str):
        cursor = transcript.textCursor()
        cursor.movePosition(QTextCursor.End)
        transcript.setTextCursor(cursor)
        transcript.insertPlainText(delta)

    def _on_done():
        entry.setEnabled(True)
        send_btn.setEnabled(True)
        entry.setFocus()

    bridge.chunk.connect(_append_delta)
    bridge.done.connect(_on_done)

    def do_send():
        text = entry.text().strip()
        if not text:
            return
        transcript.append(f"<b>Sen:</b> {text}")
        entry.clear()
        transcript.append("<b>ZeRo:</b> ")  # cevap bu satıra akacak
        entry.setEnabled(False)
        send_btn.setEnabled(False)

        def work():
            try:
                view_model.send_stream(text, lambda d: bridge.chunk.emit(d))
            except Exception as e:  # noqa: BLE001
                bridge.chunk.emit(f"(Bir sorun oldu: {e})")
            bridge.done.emit()

        threading.Thread(target=work, daemon=True).start()

    send_btn.clicked.connect(do_send)
    entry.returnPressed.connect(do_send)

    qss = Path(__file__).with_name("style.qss")
    if qss.exists():
        win.setStyleSheet(qss.read_text(encoding="utf-8"))

    return win
