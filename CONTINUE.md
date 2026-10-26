# ZeRo — Başka Bilgisayarda Devam Etme Rehberi

Bu belge, ZeRo'yu yeni bir bilgisayarda kurup kaldığın yerden devam etmen için.

## 1. Projeyi al

```
git clone https://github.com/OmerFarukErgun51/Zero_AI.git
cd Zero_AI
```

## 2. Kurulum

1. **Ollama** kur: <https://ollama.com/download>
2. **Modelleri indir** (bir kez, internet ister):
   ```
   ollama pull qwen2.5:3b
   ollama pull nomic-embed-text
   ```
3. **Python ortamı** (venv taşınmaz, yeniden kurulur):
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

## 3. Çalıştır

```
python run_zero.py
```
veya `ZeRo-Baslat.bat` dosyasına çift tıkla.

## 4. Claude ile çalışmaya devam

Bu projeyi geliştirirken kullandığımız **iş akışı skilleri** `.claude/skills/`
klasörüne gömülü (superpowers: brainstorming, writing-plans, executing-plans,
test-driven-development, requesting-code-review, systematic-debugging, vb.).
Bu repoyu Claude Code ile açınca bu skiller **proje skili** olarak görünür ve
aynı disiplinle (önce tasarım → plan → test-önce kod → inceleme) devam edebiliriz.

> Not: Skiller aslında "superpowers" Claude Code eklentisinin parçası. Küresel
> olarak da kurmak istersen Claude Code eklenti yöneticisinden superpowers'ı
> kurabilirsin; ama repodaki kopya da iş görür.

## Nerede kaldık (durum)

ZeRo v1 **çalışır durumda**, offline, GitHub'da güncel. Özellikler:
- Sohbet (JARVIS-vari, cana yakın karakter) — **streaming** (kelime kelime akış)
- **Bilgisayar araçları (ajan):** "şu dosya nerede?", "bilgisayarım/laptopum
  hakkında bilgi" → ZeRo gerçekten dosya arar / sistem bilgisini okur
- Outlook mail + takvim okuma (salt-okunur + cevap taslağı; göndermez)
- Günlük plan + hatırlatma, sabah brifingi, mola/su dürtmeleri
- Excel / PowerPoint / Word üretimi (offline)
- **RAG:** tepsi "Belge öğret" ile kendi `.txt` belgelerini öğretirsin
- Kalıcı hafıza + kişiselleşme (her açılışta sıfırdan başlamaz)
- Ekran OCR + WhatsApp/dosya içe aktarma, gün boyu etkinlik takibi + gün sonu formu
- Sistem tepsisi + HUD sohbet penceresi, otomatik başlatma

Varsayılan model **qwen2.5:3b** (CPU'da hızlı). `config.json` ile `gemma3:4b`
(Türkçesi daha iyi) veya `qwen3:4b`'ye geçilebilir.

## Sıradaki fikirler (yol haritası)

- **gemma3:4b**'ye geçmek (daha düzgün Türkçe)
- Daha fazla araç: dosya okuma/özetleme, uygulama açma, web araması
- RAG'ı PDF/Word öğrenecek şekilde genişletmek
- v1.5 ses aşaması: sesli konuşma + toplantı kaydı & özeti (sistem sesi, Whisper)
- Tepsiye net "Otomatik başlat" düğmesi

## Kurallar (tercihler)

- Commit mesajları: **önek yok** (feat/fix/chore yok), **imza yok**, sade kısa İngilizce.
- Yeni projeler D:\Projects'te (OneDrive'da değil).
- Test: `python -m pytest` (109 test geçiyor).
