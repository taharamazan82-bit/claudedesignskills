@echo off
REM Alfred teshis araci — cift tikla calistir.
REM .env okunuyor mu, Groq anahtari gecerli mi, internet var mi — hepsini test eder.

cd /d "%~dp0"
chcp 65001 >nul

echo ==================================================
echo   ALFRED TESHIS
echo ==================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo [X] Python bulunamadi. Once Python 3 kur: https://python.org/downloads
  echo.
  pause
  exit /b 1
)

if exist ".venv\Scripts\activate.bat" call .venv\Scripts\activate.bat

echo [1] .env dosyasi var mi?
if exist ".env" (
  echo     EVET - .env bulundu.
) else (
  echo     HAYIR - .env yok! Bu klasorde .env dosyasi olustur ve icine:
  echo     GROQ_API_KEY=senin_anahtarin
  echo.
  pause
  exit /b 1
)
echo.

echo [2] Groq baglantisi test ediliyor...
echo --------------------------------------------------
python tools\llm_router.py --json "Tek kelimeyle selam ver."
echo --------------------------------------------------
echo.
echo Yukaridaki ciktiyi kopyalayip yardim icin paylas.
echo   - "no API key set"  -^> .env okunmuyor (adi .env.txt olabilir)
echo   - "HTTP 401/403"     -^> anahtar gecersiz, yenisini al
echo   - "network: ..."     -^> internet/guvenlik duvari
echo   - "ok": true         -^> HER SEY CALISIYOR!
echo.
pause
