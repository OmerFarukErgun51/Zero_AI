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

    # Cevap arka plan thread'inde üretilir; sonuç sinyalle ana thread'e döner
    # (böylece pencere donmaz).
    class _Bridge(QObject):
        reply_ready = Signal(str)

    bridge = _Bridge()

    def _on_reply(reply: str):
        transcript.append(f"<b>ZeRo:</b> {reply}")
        entry.setEnabled(True)
        send_btn.setEnabled(True)
        entry.setFocus()

    bridge.reply_ready.connect(_on_reply)

    def do_send():
        text = entry.text().strip()
        if not text:
            return
        transcript.append(f"<b>Sen:</b> {text}")
        entry.clear()
        transcript.append("<i>ZeRo yazıyor…</i>")
        entry.setEnabled(False)
        send_btn.setEnabled(False)

        def work():
            try:
                reply = view_model.send(text)
            except Exception as e:  # noqa: BLE001
                reply = f"(Bir sorun oldu: {e})"
            bridge.reply_ready.emit(reply)

        threading.Thread(target=work, daemon=True).start()

    send_btn.clicked.connect(do_send)
    entry.returnPressed.connect(do_send)

    qss = Path(__file__).with_name("style.qss")
    if qss.exists():
        win.setStyleSheet(qss.read_text(encoding="utf-8"))

    return win
