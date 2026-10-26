"""Beyin katmanı — Ollama istemcisi (sohbet + embedding), isteğe bağlı yükleme."""

from __future__ import annotations

import re
from dataclasses import dataclass

from zero.config import Config

_THINK_RE = re.compile(r"<think>.*?</think>", re.DOTALL)


@dataclass
class BrainStatus:
    ok: bool
    message: str


def _default_client():
    import ollama

    return ollama.Client()


def _model_names(listing) -> list[str]:
    models = listing["models"] if isinstance(listing, dict) else getattr(listing, "models", [])
    names: list[str] = []
    for m in models:
        if isinstance(m, dict):
            name = m.get("model") or m.get("name")
        else:
            name = getattr(m, "model", None) or getattr(m, "name", None)
        if name:
            names.append(name)
    return names


def _content(resp) -> str:
    if isinstance(resp, dict):
        text = resp["message"]["content"]
    else:
        text = resp.message.content
    # Açılış etiketi şablon tarafından yenmiş olabilir; </think> sonrasını al.
    if "</think>" in text:
        text = text.rsplit("</think>", 1)[-1]
    return _THINK_RE.sub("", text).strip()


def _embedding(resp) -> list[float]:
    if isinstance(resp, dict):
        return list(resp["embedding"])
    return list(resp.embedding)


class Brain:
    def __init__(self, config: Config, client=None):
        self.config = config
        self._client = client if client is not None else _default_client()

    def is_available(self) -> BrainStatus:
        try:
            listing = self._client.list()
        except Exception:
            return BrainStatus(
                False,
                "Ollama çalışmıyor gibi görünüyor. Lütfen Ollama'yı başlat "
                "(https://ollama.com) ve tekrar dene.",
            )
        names = _model_names(listing)
        if self.config.model not in names:
            return BrainStatus(
                False,
                f"'{self.config.model}' modeli bulunamadı. Şunu çalıştır: "
                f"ollama pull {self.config.model}",
            )
        return BrainStatus(True, "ZeRo hazır.")

    def chat(self, messages: list[dict], stream: bool = False) -> str:
        messages = self._no_think(messages)
        kwargs = dict(
            model=self.config.model,
            messages=messages,
            keep_alive=self.config.keep_alive,
            stream=stream,
            think=False,  # qwen3 gibi düşünen modellerde hızı için düşünmeyi kapat
        )
        try:
            resp = self._client.chat(**kwargs)
        except TypeError:
            # Eski ollama istemcisi 'think' parametresini tanımıyorsa onsuz dene
            kwargs.pop("think")
            resp = self._client.chat(**kwargs)
        return _content(resp)

    def _no_think(self, messages: list[dict]) -> list[dict]:
        """qwen3 için son kullanıcı mesajına '/no_think' ekler (düşünmeyi kapatır)."""
        if "qwen3" not in self.config.model:
            return messages
        out = [dict(m) for m in messages]
        for m in reversed(out):
            if m.get("role") == "user":
                if "/no_think" not in m["content"]:
                    m["content"] = m["content"] + " /no_think"
                break
        return out

    def chat_stream(self, messages: list[dict]):
        """Cevabı parça parça (delta) üretir — arayüzde kelime kelime akması için."""
        messages = self._no_think(messages)
        kwargs = dict(
            model=self.config.model,
            messages=messages,
            keep_alive=self.config.keep_alive,
            stream=True,
            think=False,
        )
        try:
            stream = self._client.chat(**kwargs)
        except TypeError:
            kwargs.pop("think")
            stream = self._client.chat(**kwargs)
        for chunk in stream:
            if isinstance(chunk, dict):
                delta = chunk.get("message", {}).get("content", "")
            else:
                delta = getattr(getattr(chunk, "message", None), "content", "") or ""
            if delta:
                yield delta

    def chat_tools(self, messages: list[dict], tools: list):
        """Modeli araçlarla çağırır; dönen mesajı (içerik + olası tool_calls) döndürür."""
        messages = self._no_think(messages)
        kwargs = dict(
            model=self.config.model,
            messages=messages,
            keep_alive=self.config.keep_alive,
            tools=tools,
            think=False,
        )
        try:
            resp = self._client.chat(**kwargs)
        except TypeError:
            kwargs.pop("think")
            resp = self._client.chat(**kwargs)
        return resp["message"] if isinstance(resp, dict) else resp.message

    def embed(self, text: str) -> list[float]:
        resp = self._client.embeddings(
            model=self.config.embed_model,
            prompt=text,
        )
        return _embedding(resp)
