"""Beyin katmanı — Ollama istemcisi (sohbet + embedding), isteğe bağlı yükleme."""

from __future__ import annotations

from dataclasses import dataclass

from zero.config import Config


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
        return resp["message"]["content"]
    return resp.message.content


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
        resp = self._client.chat(
            model=self.config.model,
            messages=messages,
            keep_alive=self.config.keep_alive,
            stream=stream,
        )
        return _content(resp)

    def embed(self, text: str) -> list[float]:
        resp = self._client.embeddings(
            model=self.config.embed_model,
            prompt=text,
        )
        return _embedding(resp)
