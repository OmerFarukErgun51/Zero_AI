from zero.memory.store import MemoryStore
from zero.memory.profile import update_profile


class FakeBrain:
    def __init__(self, reply="Kısa cevap sever."):
        self.reply = reply
        self.calls = []

    def chat(self, messages, **kwargs):
        self.calls.append(messages)
        return self.reply


def _store(tmp_path):
    return MemoryStore(tmp_path / "zero.sqlite3")


def test_summary_stored(tmp_path):
    s = _store(tmp_path)
    s.add_message("omer", "user", "merhaba")
    out = update_profile(s, FakeBrain("Kısa cevap sever."), "omer")
    assert out == "Kısa cevap sever."
    assert s.get_profile_summary("omer") == "Kısa cevap sever."


def test_noop_when_no_messages(tmp_path):
    s = _store(tmp_path)
    brain = FakeBrain()
    out = update_profile(s, brain, "omer")
    assert out == ""
    assert brain.calls == []


def test_prompt_is_turkish_and_includes_messages(tmp_path):
    s = _store(tmp_path)
    s.add_message("omer", "user", "futbol seviyorum")
    brain = FakeBrain()
    update_profile(s, brain, "omer")
    sent = brain.calls[0]
    blob = " ".join(m["content"] for m in sent)
    assert "futbol seviyorum" in blob
    assert "profil" in blob.lower()
