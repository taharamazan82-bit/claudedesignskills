# Alfred — Yerel/Ücretsiz Sanal Asistan

Jarvis benzeri, uzun vadede token/API parası ödemeden çalışacak, sesli + yazılı
etkileşimli bir asistan. İlke: **"Python yapar, AI yönetir"** — her yetenek bağımsız
bir `.py` aracı (AI olmadan da çalışır), AI yalnızca hangi aracı çağıracağına karar verir.

> Tam mimari ve yol haritası: `../` plan dosyası. Bu README kurulum + durum içindir.

## Zero-touch kurulum (Windows hedef)
Elle wiring yok. Tek gereken **bir kez** ücretsiz Groq anahtarını `.env`'e yapıştırmak.

```bash
python3 setup.py                       # .env oluşturur, araçları hazırlar, önkoşulları kontrol eder
# .env içine GROQ_API_KEY=... yapıştır (tek manuel adım)
python3 tools/llm_router.py "Merhaba Alfred"     # beyin, AI olmadan CLI'dan çalışır
```

Backend (arayüz köprüsü):
```bash
cd backend && pip install -r requirements.txt && uvicorn app:app --port 8000
```

## Şu anki durum (modüler — teker teker)
- [x] **Modül 0 — Temel & zero-touch iskelet**: yapı, config, docs, `.gitignore`, `.env.example`, `setup.py`.
- [x] **Modül 1 — Beyin & router**: `tools/llm_router.py` (Groq→Gemini→OpenRouter fallback), `tools/run_tool.py`
      (güvenlik allowlist), `backend/app.py` (FastAPI + WebSocket), `n8n/chat-flow.json`. Testler: `tools/tests/`.
- [ ] Modül 2 — Three.js etkileşimli arayüz (avatar + araç dock'u, lite mod)
- [ ] Modül 3 — Ses (Groq Whisper STT + Piper TTS) + "Alfred" wake-word
- [ ] Modül 4 — Web araştırma
- [ ] Modül 5 — Video düzenleme + YouTube yükleme + takip
- [ ] Modül 5.5 — Sistem kontrolü (uygulama aç/kapat/ayar — hazır kod modülleri)
- [ ] Modül 6 — Genişletme & dayanıklılık

## Test
```bash
python3 -m unittest discover -s tools/tests -v     # sağlayıcılar mock'lu, kota yakmaz
```

## Güvenlik / gizlilik
- API anahtarları **asla kodda değil** — `.env` (gitignore'lu) / Windows Credential Manager; yalnızca backend okur, tarayıcıya gitmez.
- AI serbest shell komutu üretmez; yalnızca `run_tool.py` allowlist'inden seçim yapar → **injection yüzeyi kapalı**.
- Her şey localhost; dışa açık uç yok.
