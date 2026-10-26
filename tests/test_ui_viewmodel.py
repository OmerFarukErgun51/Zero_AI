from zero.memory.store import MemoryStore
from zero.ui.chat_window import ChatViewModel


class FakeApp:
    def __init__(self, store, reply="cevap"):
        self.store = store
        self.reply = reply
        self.calls = []

    def chat_turn(self, profile, text):
        self.calls.append((profile, text))
        return self.reply

    def chat_turn_stream(self, profile, text, on_chunk):
        self.calls.append((profile, text))
        for part in ["ce", "vap"]:
            on_chunk(part)
        return self.reply


def test_send_delegates_to_app(tmp_path):
    app = FakeApp(MemoryStore(tmp_path / "zero.sqlite3"), reply="Buyur Ömer.")
    vm = ChatViewModel(app, "omer")
    out = vm.send("selam")
    assert out == "Buyur Ömer."
    assert app.calls == [("omer", "selam")]


def test_send_stream_delivers_chunks(tmp_path):
    app = FakeApp(MemoryStore(tmp_path / "zero.sqlite3"), reply="cevap")
    vm = ChatViewModel(app, "omer")
    chunks = []
    full = vm.send_stream("selam", chunks.append)
    assert chunks == ["ce", "vap"]
    assert full == "cevap"


def test_history_reads_store(tmp_path):
    store = MemoryStore(tmp_path / "zero.sqlite3")
    store.add_message("omer", "user", "eski mesaj")
    vm = ChatViewModel(FakeApp(store), "omer")
    assert [m.text for m in vm.history()] == ["eski mesaj"]
