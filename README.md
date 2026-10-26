# ZeRo 🤖

A calm, friendly, JARVIS-inspired desktop AI assistant that lives in your system
tray and runs **fully offline**. ZeRo reads your Outlook mail and calendar
(read-only), builds and reminds you of your daily plan, nudges you to take breaks,
generates Excel/PowerPoint/Word files, reads your screen or exported chats on
request, tracks your day, and remembers you across sessions — so it never starts
from scratch.

Everything runs locally on your machine. Nothing is sent to any company; only the
one-time model download needs the internet.

## Features (v1)

- **Chat** — talk to ZeRo, ask for ideas and advice, in its calm JARVIS-like voice.
- **Mail & calendar** — reads classic Outlook (read-only); drafts replies for you to
  review, but never sends mail and never writes to your calendar.
- **Daily plan & reminders** — give your plan in free text or a short form; ZeRo
  merges it with your meetings and reminds you at the right time.
- **Morning briefing** — a short summary every time your computer starts.
- **Health nudges** — gentle break / water / eye-rest reminders.
- **Documents** — generates Excel, PowerPoint and Word files offline.
- **Memory** — persistent local memory; learns your profile over time for better
  suggestions. Explicitly teach it with "remember this".
- **Screen & imports** — reads your current screen (OCR) or an exported WhatsApp
  `.txt` / saved mail on request.
- **Activity tracking** — lightweight window tracking + an editable end-of-day report.

## Requirements

- Windows 10/11, Python 3.11+
- [Ollama](https://ollama.com/download) with a small local model
- Classic Outlook (desktop) for the mail/calendar features
- Tesseract (optional) for screen OCR

## Setup

1. Install Ollama, then pull the models (one-time, needs internet):
   ```
   ollama pull qwen2.5:3b
   ollama pull nomic-embed-text
   ```
   (`qwen2.5:3b` is a good fast default for a CPU-only machine. You can switch it
   to `gemma3:4b` or `qwen3:4b` in `config.json` if you have more power.)
2. Install Python dependencies:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Run

```
python run_zero.py
```

ZeRo appears in the system tray. Use the tray menu to show/hide the chat window,
enter a plan, create a presentation, read the screen, import a file, get the
end-of-day report, pause, or enable auto-start on boot.

## Privacy

All data — mail, conversations, activity — stays on your machine. ZeRo uploads
nothing. The model and embeddings run locally through Ollama; no internet is
required after the initial model download.

## Development

```
python -m pytest
```

- Design doc: `docs/2026-10-26-zero-masaustu-asistani-tasarim.md`
- Implementation plan: `docs/superpowers/plans/2026-10-26-zero-v1.md`

## Roadmap

- **v1.5 (audio):** voice conversation (offline Whisper + TTS) and meeting
  recording & summary (captures system audio, transcribes, produces a "what was
  discussed" form).
- **v2+:** Teams (if the account allows), web search / weather.
