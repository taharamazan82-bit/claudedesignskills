# Alfred Araç (CLI) Konvansiyonları

Her `tools/*.py` bağımsız çalışır (AI olmadan) ve şu kurallara uyar. Böylece n8n
ve backend onları tek biçimde tüketir; test kotayı yakmadan yapılır.

## Zorunlu
- İlk satır: `#!/usr/bin/env python3`; dosya executable (`chmod +x`).
- Yalnızca **Python 3 standart kütüphanesi** (pip yok) — zero-touch kurulum için.
- Modül düzeyinde docstring: amaç + kullanım örnekleri.
- `--json`: makine-okur çıktı (n8n/backend için). İnsan çıktısı varsayılan.
- `--dry-run`: ağ/yan-etki olmadan ne yapacağını gösterir (kotayı/veriyi korur).
- `--help`: argparse otomatik sağlar.

## Çıktı sözleşmesi
- Başarı JSON'u: `{"ok": true, ...}`.
- Hata JSON'u: `{"ok": false, "error": "<kod>", "detail": "..."}`.
- İnsan-okur hata (stderr): **problem + neden + çözüm** üç satırı.

## Exit kodları
- `0` başarı · `2` çalışma-zamanı başarısız · `3` geçersiz istek (tekrar denenmez)
  · `4` kullanım/argüman hatası.

## Güvenlik
- Araçlar `run_tool.py` allowlist'i üzerinden çağrılır; AI doğrudan script çağırmaz.
- `subprocess` her zaman **liste argümanı** ile (asla `shell=True`, asla string).
- Sırlar `.env`/keyring'den okunur; log/çıktı anahtarları maskeler.

## Test
- Birim testleri sağlayıcı/ağ çağrılarını **mock**'lar (bkz. `tools/tests/`).
- Çalıştır: `python3 -m unittest discover -s tools/tests`.
