# راهنمای راه‌اندازی و تکمیل `.env`

این راهنما برای همین Repository است. هیچ مقدار واقعی از Token، Password، API Hash یا Session را در Chat، Issue یا GitHub وارد نکنید.

## 1) ابتدا فایل `.env` را بسازید

در ریشه پروژه:

```bash
cp .env.example .env
chmod 600 .env
```

در ویندوز، فایل را با نام دقیق `.env` بسازید و آن را از Git خارج نگه دارید.

---

## 2) PostgreSQL با پورت 5431

### حالت A: PostgreSQL روی خود سیستم اجرا می‌شود

اگر Database شما روی `127.0.0.1:5431` است، این مقدار درست است:

```env
DATABASE_URL=postgresql+asyncpg://musicbot:YOUR_DB_PASSWORD@127.0.0.1:5431/musicbot
```

اگر Password کاراکترهایی مثل `@`، `:`، `/` یا `#` دارد، آن را URL-Encode کنید.

بررسی اتصال:

```bash
psql -h 127.0.0.1 -p 5431 -U musicbot -d musicbot
```

### حالت B: PostgreSQL با Docker Compose اجرا می‌شود و Bot روی Host است

در `.env`:

```env
POSTGRES_HOST_PORT=5431
REDIS_HOST_PORT=16379
DATABASE_URL=postgresql+asyncpg://musicbot:musicbot@127.0.0.1:5431/musicbot
```

سپس:

```bash
docker compose up -d postgres redis
docker compose ps
```

در این حالت پورت بیرونی `5431` است، اما پورت داخلی Container همچنان `5432` است.

### حالت C: Bot هم داخل Docker Compose اجرا می‌شود

در این حالت از `localhost` استفاده نکنید؛ چون `localhost` داخل Container خود Bot است:

```env
DATABASE_URL=postgresql+asyncpg://musicbot:musicbot@postgres:5432/musicbot
REDIS_URL=redis://redis:6379/0
```

### نکته مهم

- Bot روی Host: `127.0.0.1:5431`
- Bot داخل Docker: `postgres:5432`
- Redis روی Host: `127.0.0.1:16379`
- Redis داخل Docker: `redis:6379`

---

## 3) Redis

برای Redis محلی یا Docker با Port Mapping:

```env
REDIS_URL=redis://127.0.0.1:16379/0
```

برای Bot داخل Compose:

```env
REDIS_URL=redis://redis:6379/0
```

بررسی:

```bash
redis-cli -h 127.0.0.1 -p 16379 ping
```

خروجی باید این باشد:

```text
PONG
```

---

## 4) Bot Account تلگرام

در تلگرام با `@BotFather`:

1. اجرای `/newbot`
2. انتخاب نام و Username
3. دریافت Bot Token
4. قرار دادن Token فقط در `.env`:

```env
BOT_TOKEN=توکن_واقعی_اینجا
```

### تنظیمات پیشنهادی BotFather

- `/setdescription`
- `/setabouttext`
- `/setuserpic`
- `/setcommands`
- `/setprivacy`

برای دریافت متن فارسی مثل `پخش لینک` در گروه، Privacy Mode را Disable کنید یا Bot را Admin کنید. کامندهای رسمی تلگرام باید انگلیسی باشند:

```text
play - پخش آهنگ یا لینک
pause - توقف موقت
resume - ادامه پخش
skip - آهنگ بعدی
queue - نمایش صف
now - آهنگ در حال پخش
stop - توقف پخش
playlist - مدیریت لیست پخش
help - راهنما
```

### Permissionهای Bot در گروه

بسته به قابلیت فعال:

- ارسال پیام
- ویرایش پیام‌های خودش
- حذف پیام‌های خودش یا Commandها در صورت نیاز
- Pin کردن پنل در صورت نیاز

Bot معمولی مسئول ارسال Command و پنل است؛ ورود به Voice Chat با Assistant انجام می‌شود.

---

## 5) Assistant User Account

Assistant باید یک اکانت معمولی تلگرام باشد، نه Bot Account. بهتر است اکانت اختصاصی باشد و از اکانت شخصی اصلی استفاده نشود.

از `my.telegram.org`:

1. ورود به بخش API Development Tools
2. ساخت Application
3. دریافت `API_ID`
4. دریافت `API_HASH`

مقادیر را فقط در `.env` قرار دهید:

```env
API_ID=عدد_واقعی
API_HASH=مقدار_واقعی
```

سپس Dependency تلگرام را نصب کنید:

```bash
python -m pip install -e ".[telegram]"
```

Session را روی سیستم امن خودتان بسازید:

```bash
PYTHONPATH=src python -m music_player_bot.tools.generate_session
```

این ابزار شماره، کد ورود و در صورت فعال‌بودن 2FA را به‌صورت محلی می‌گیرد و `ASSISTANT_SESSION` را در `.env` می‌نویسد. مقدار Session چاپ نمی‌شود.

```env
ASSISTANT_SESSION=مقدار_تولیدشده_محلی
```

هرگز این مقدار را در Chat، GitHub یا Screenshot قرار ندهید.

---

## 6) Test Group و Voice Chat

1. یک گروه خصوصی تست بسازید.
2. Bot را اضافه و در صورت نیاز Admin کنید.
3. Assistant را اضافه کنید.
4. یک Voice Chat فعال بسازید.
5. Assistant را در Call قادر به صحبت/مدیریت کنید.
6. شناسه گروه را در صورت نیاز در `.env` بنویسید:

```env
TEST_CHAT_ID=-1001234567890
```

این مقدار Secret نیست، اما بهتر است در Log عمومی منتشر نشود.

---

## 7) FFmpeg

FFmpeg برای Decode، Transcode و پخش Media لازم است.

### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install -y ffmpeg
```

### macOS

```bash
brew install ffmpeg
```

### Windows

```powershell
winget install Gyan.FFmpeg
```

بررسی:

```bash
ffmpeg -version
```

در `.env`:

```env
FFMPEG_PATH=ffmpeg
```

اگر مسیر اختصاصی دارید، مسیر کامل بدهید:

```env
FFMPEG_PATH=/usr/bin/ffmpeg
```

---

## 8) تنظیمات عمومی پیشنهادی برای شروع

```env
ENVIRONMENT=development
LOG_LEVEL=INFO
TEMP_MEDIA_DIR=./runtime/media
MAX_TRACK_DURATION_SECONDS=7200
MAX_QUEUE_SIZE=100
```

برای اولین تست این Feature Flagها خاموش بمانند:

```env
ENABLE_EXTERNAL_PROVIDERS=false
ENABLE_VIDEO=false
```

بعد از موفقیت Audio Playback POC، هر قابلیت جداگانه فعال و تست می‌شود.

---

## 9) YouTube

برای Search و Metadata رسمی:

1. ورود به Google Cloud Console
2. ساخت Project
3. فعال‌کردن YouTube Data API v3
4. ساخت API Key
5. محدودکردن Key به IP یا APIهای لازم
6. قرار دادن آن در `.env`:

```env
YOUTUBE_API_KEY=کلید_واقعی
```

برای Resolve مستقیم، ممکن است Provider به API Key نیاز نداشته باشد؛ اما این به معنی تضمین پایداری یا مجازبودن هر نوع استفاده نیست. محتوای دارای Copyright، Private یا محدودشده نباید دور زده شود.

---

## 10) Spotify

Spotify برای نسخه فعلی فقط Metadata/Official Link/Playlist Import است؛ Full Track در Telegram Voice Chat وعده قطعی نیست.

برای Metadata و OAuth آینده:

1. ورود به Spotify Developer Dashboard
2. ساخت App
3. دریافت Client ID و Client Secret
4. اضافه‌کردن Redirect URI دقیق
5. تکمیل `.env`:

```env
SPOTIFY_CLIENT_ID=client_id_واقعی
SPOTIFY_CLIENT_SECRET=client_secret_واقعی
SPOTIFY_REDIRECT_URI=https://YOUR_DOMAIN.example/spotify/callback
```

برای نسخه Metadata-only، Redirect URI ممکن است هنوز لازم نباشد؛ آن را برای OAuth آینده نگه می‌داریم.

Access Token و Refresh Token را در `.env` دائمی قرار ندهید؛ در صورت اضافه‌شدن OAuth کاربر، باید رمزنگاری‌شده و per-user ذخیره شوند.

---

## 11) SoundCloud، Instagram، Vimeo، Twitch و TikTok

در نسخه اولیه برای URLهای عمومی، Credential جداگانه در `.env` لازم نیست:

- SoundCloud: `BEST_EFFORT`
- Vimeo: `BEST_EFFORT`
- Instagram عمومی: `BEST_EFFORT`
- Twitch: `BEST_EFFORT`
- TikTok عمومی: `BEST_EFFORT`

محتوای Private، Login-only یا Protected بدون مسیر رسمی احراز هویت فعال نمی‌شود. Cookie Browser یا Session سایت را در `.env` یا Git وارد نکنید.

---

## 12) Telegram Webhook اختیاری

رابط کاربری پروژه Telegram Native Panel است و Mini App/Web App در Scope فعلی نیست.

برای Long Polling این مقادیر خالی بمانند:

```env
WEBHOOK_BASE_URL=
WEBHOOK_SECRET=
```

برای Production با Webhook:

```env
WEBHOOK_BASE_URL=https://bot.YOUR_DOMAIN.example
WEBHOOK_SECRET=یک_مقدار_تصادفی_بلند
```

`WEBHOOK_SECRET` را با Password Manager یا Secret Generator بسازید و در Chat ارسال نکنید.

---

## 13) نمونه `.env` برای اجرای Bot روی Host

این نمونه را کپی نکنید؛ فقط ساختار را نشان می‌دهد:

```env
BOT_TOKEN=...
API_ID=...
API_HASH=...
ASSISTANT_SESSION=...

ENVIRONMENT=development
LOG_LEVEL=INFO
FFMPEG_PATH=ffmpeg
TEMP_MEDIA_DIR=./runtime/media
MAX_TRACK_DURATION_SECONDS=7200
MAX_QUEUE_SIZE=100

DATABASE_URL=postgresql+asyncpg://musicbot:YOUR_DB_PASSWORD@127.0.0.1:5431/musicbot
REDIS_URL=redis://127.0.0.1:16379/0
POSTGRES_HOST_PORT=5431
REDIS_HOST_PORT=16379

WEBHOOK_BASE_URL=
WEBHOOK_SECRET=

SPOTIFY_CLIENT_ID=
SPOTIFY_CLIENT_SECRET=
SPOTIFY_REDIRECT_URI=
YOUTUBE_API_KEY=
TEST_CHAT_ID=

ENABLE_EXTERNAL_PROVIDERS=false
ENABLE_VIDEO=false
```

---

## 14) بررسی نهایی قبل از ادامه پروژه

```bash
PYTHONPATH=src python -m music_player_bot.tools.check_runtime
```

سپس تست‌های آفلاین:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

خروجی Runtime باید برای این موارد `OK` باشد:

```text
BOT_TOKEN
API_ID
API_HASH
ASSISTANT_SESSION
FFMPEG
```

بعد از آن، Agent می‌تواند Playback Proof of Concept واقعی را اجرا کند. Credential واقعی را در Chat ارسال نکنید؛ فقط نتیجه بررسی را اعلام کنید.
