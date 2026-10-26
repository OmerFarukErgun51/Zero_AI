# ZeRo 🤖

Masaüstünde yaşayan, **tamamen offline** çalışan, cana yakın ve sakin karakterli
(JARVIS ilhamlı) yapay zeka asistanı. Mailini/takvimini okur, günlük planını kurup
hatırlatır, mola verdirir, Excel/PowerPoint/Word üretir, seni zamanla tanır ve
her açılışta sıfırdan başlamaz.

## Kurulum

1. **Ollama'yı kur** (yerel yapay zeka motoru): <https://ollama.com/download>
2. **Modelleri indir** (bir kez, internet gerekir):
   ```
   ollama pull qwen3:4b
   ollama pull nomic-embed-text
   ```
   (Dilersen `qwen3:4b` yerine `gemma3:4b` deneyip `config.json` içinde `model`'i değiştir.)
3. **Python bağımlılıkları:**
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. **OCR için (isteğe bağlı):** Tesseract kur ve Türkçe dil paketini ekle
   (ekran okuma özelliği için).

## Çalıştırma

```
python run_zero.py
```

ZeRo sistem tepsisinde belirir. Bilgisayar açılışında otomatik başlaması için
tepsi menüsünden "Otomatik başlat"ı aç.

## Gizlilik

Her şey bilgisayarında kalır. Mail/sohbet/takip verisi dışarı gönderilmez.
Ollama ve modeller yerelde çalışır; ilk model indirmesi dışında internet gerekmez.

## Geliştirme

```
python -m pytest
```

Tasarım: `docs/2026-10-26-zero-masaustu-asistani-tasarim.md`
Plan: `docs/superpowers/plans/2026-10-26-zero-v1.md`
