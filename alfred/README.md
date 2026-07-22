# Alfred — Yerel/Ücretsiz Sanal Asistan

Jarvis benzeri, uzun vadede token/API parası ödemeden çalışacak, sesli + yazılı
etkileşimli bir asistan. İlke: **"Python yapar, AI yönetir"** — her yetenek bağımsız
bir `.py` aracı (AI olmadan da çalışır), AI yalnızca hangi aracı çağıracağına karar verir.

> Tam mimari ve yol haritası: `../` plan dosyası. Bu README kurulum + durum içindir.

## Zero-touch kurulum (Windows)
Elle wiring yok. Tek gereken **bir kez** ücretsiz Groq anahtarını `.env`'e yapıştırmak.

**En kolay yol — çift tıkla:** `Alfred.bat`
İlk çalıştırmada sanal ortamı kurar, backend bağımlılıklarını yükler, backend + 3D arayüzü
başlatır ve tarayıcıda `http://127.0.0.1:5173` açılır. Sonraki çalıştırmalar anında.

Öncesinde tek sefer: `.env` içine `GROQ_API_KEY=...` yapıştır (anahtar `console.groq.com`'dan ücretsiz).

**Elle / diğer OS:**
```bash
python3 setup.py                              # .env + önkoşul kontrolü
python3 tools/llm_router.py "Merhaba Alfred"  # beyin, AI olmadan CLI'dan çalışır
python3 start.py                              # backend + frontend birlikte
```

## Şu anki durum (modüler — teker teker)
- [x] **Modül 0 — Temel & zero-touch iskelet**: yapı, config, docs, `.gitignore`, `.env.example`, `setup.py`.
- [x] **Modül 1 — Beyin & router**: `tools/llm_router.py` (Groq→Gemini→OpenRouter fallback), `tools/run_tool.py`
      (güvenlik allowlist), `backend/app.py` (FastAPI + WebSocket), `n8n/chat-flow.json`. Testler: `tools/tests/`.
- [x] **Modül 2 — Three.js etkileşimli arayüz**: `frontend/` (Vite+React+R3F), animasyonlu Alfred avatarı
      (durum makinesi: idle/dinliyor/düşünüyor/konuşuyor/hata), sohbet paneli, araç dock'u, **lite mod** (zayıf donanım). `npm run build` ✓.
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
