import pytest

from zero.config import Config
from zero.brain import Brain


class FakeClient:
    def __init__(self, models=("qwen3:4b", "nomic-embed-text"), raise_on_list=False):
        self._models = list(models)
        self._raise_on_list = raise_on_list
        self.chat_kwargs = None

    def chat(self, **kwargs):
        self.chat_kwargs = kwargs
        return {"message": {"content": "merhaba Ömer"}}

    def list(self):
        if self._raise_on_list:
            raise ConnectionError("refused")
        return {"models": [{"model": m} for m in self._models]}

    def embeddings(self, **kwargs):
        return {"embedding": [0.1, 0.2, 0.3]}


def _brain(client):
    return Brain(Config(), client=client)


def test_chat_sends_model_and_keep_alive():
    fake = FakeClient()
    out = _brain(fake).chat([{"role": "user", "content": "selam"}])
    assert fake.chat_kwargs["model"] == "qwen2.5:3b"
    assert fake.chat_kwargs["keep_alive"] == "30m"
    assert out == "merhaba Ömer"


def test_chat_disables_thinking():
    # qwen3 gibi "düşünen" modeller CPU'da yavaş; sohbet için düşünme kapalı olmalı
    fake = FakeClient()
    _brain(fake).chat([{"role": "user", "content": "selam"}])
    assert fake.chat_kwargs["think"] is False


def test_chat_appends_no_think_for_qwen():
    fake = FakeClient()
    Brain(Config(model="qwen3:4b"), client=fake).chat([{"role": "user", "content": "selam"}])
    assert "/no_think" in fake.chat_kwargs["messages"][-1]["content"]


def test_content_strips_think_block():
    from zero.brain import _content

    resp = {"message": {"content": "<think>uzun uzun düşünce</think>\nMerhaba Ömer."}}
    assert _content(resp) == "Merhaba Ömer."


def test_content_strips_orphan_think_close():
    from zero.brain import _content

    resp = {"message": {"content": "düşünce metni burada\n</think>\nGerçek cevap."}}
    assert _content(resp) == "Gerçek cevap."


def test_is_available_false_when_connection_error():
    status = _brain(FakeClient(raise_on_list=True)).is_available()
    assert status.ok is False
    assert "Ollama" in status.message


def test_is_available_false_when_model_missing():
    status = _brain(FakeClient(models=("nomic-embed-text",))).is_available()
    assert status.ok is False
    assert "pull" in status.message.lower()


def test_embed_returns_vector():
    assert _brain(FakeClient()).embed("x") == [0.1, 0.2, 0.3]
