# Ücretsiz AI Sağlayıcıları — Seçim ve Kotalar

Alfred'in beyni tek bir sağlayıcıya bağlı değildir. `llm_router.py` sırayla dener,
biri kotayı doldurur/hata verirse otomatik bir sonrakine düşer. Böylece **free-tier
limitleri içinde ~sıfır maliyet** hedefi korunur.

> Kotalar sağlayıcılar tarafından zamanla değiştirilir; aşağıdaki değerler yön
> göstericidir. Kesin güncel limit için sağlayıcının kendi konsoluna bakılır.

| Sağlayıcı | Rol | Neden | Not (free tier) |
|-----------|-----|-------|-----------------|
| **Groq** | Birincil beyin + STT | Çok hızlı; Llama 3.3 70B / Qwen; **ücretsiz Whisper** | Günlük istek/token limiti; hız yüksek |
| **Google Gemini** | Yedek | Cömert ücretsiz kota, multimodal, uzun bağlam | Dakika/gün istek limiti |
| **OpenRouter** | Yedek | Tek anahtarla `:free` modeller (DeepSeek/Llama/Qwen) | `:free` modellerde düşük hız limiti |
| **Cerebras / Mistral** | İkincil yedek | Ek hız/kapasite | İsteğe bağlı eklenir |
| **Ollama** (yerel) | Çevrimdışı acil yedek | Anahtarsız, tamamen yerel | Zayıf CPU'da yavaş; küçük model |

## "Python yapar, AI yönetir" ile maliyet neden düşük?
Asıl iş (video kurgu, arama, dosya işleme, sistem kontrolü) deterministik Python
araçlarında yapılır — LLM'e gitmez. LLM yalnızca **karar/özet** için çağrılır. Bu,
çağrı sayısını düşürüp free-tier limitlerinin altında kalmayı bir tasarım hedefi yapar.

## Anahtar nasıl alınır (bir kez, tek yapıştırma)
1. Groq: https://console.groq.com → API key oluştur → kurulum sihirbazındaki kutuya yapıştır.
2. (Opsiyonel) Gemini: https://aistudio.google.com/apikey
3. (Opsiyonel) OpenRouter: https://openrouter.ai/keys

Anahtarlar `.env`'e yazılır (asla koda/committe girmez), yalnızca backend okur.

## Retry taksonomisi (llm_router)
- `200` → başarı, döndür.
- `429` / `5xx` / ağ hatası → geçici, sıradaki sağlayıcıya düş.
- `401` / `403` / `404` → sağlayıcı yanlış yapılandırılmış, atla, sıradakine geç.
- diğer `4xx` (400/422) → istek hatalı, dur ve bildir (tekrar denemek düzeltmez).
