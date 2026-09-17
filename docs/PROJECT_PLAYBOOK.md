# Music Player Bot — Project Playbook

**نسخه:** 1.0
**هدف:** یک چک‌لیست مرحله‌به‌مرحله، کم‌ابهام و قابل اجرا برای ساخت، تست، مستندسازی و انتشار ربات پخش موسیقی تلگرام.
**زبان محصول:** فارسی/RTL در نسخه اول، با قابلیت i18n.
**وضعیت فعلی:** Repository تقریباً خالی است؛ مرحله مستندسازی انجام شده و اجرای Gate 1 به ورودی امن کاربر نیاز دارد.

---

## 0) قرارداد پروژه

### 0.1 هدف محصول

ساخت یک پلتفرم پخش رسانه با هسته مستقل از تلگرام که بتواند:

- فایل‌های Telegram و URLهای مستقیم مجاز را با پایداری بالا پخش کند.
- Queue، Playlist، Favorites، History و Permission داشته باشد.
- در گروه و Private Chat پنل مدرن و ساده ارائه دهد.
- Providerهای خارجی را به‌صورت Adapter و Feature Flag اضافه کند.
- بعداً امکان اتصال به پلتفرم‌های دیگر را بدون بازنویسی Domain Core فراهم کند.

### 0.2 موارد خارج از وعده قطعی

این موارد فقط مشروط، Metadata-only یا آزمایشی هستند:

- Spotify Full Track در Telegram Voice Chat
- دورزدن DRM، Paywall، Login، Geo Restriction یا Anti-Bot
- پشتیبانی همیشگی از هر لینک خارجی
- پخش محتوای Copyright بدون حق استفاده
- تضمین Video یا Live برای تمام Providerها
- افزودن سریع Discord/WhatsApp بدون Adapter و تست مستقل

### 0.3 مدل سطح پشتیبانی Provider

| سطح | معنی |
|---|---|
| `GUARANTEED` | تست‌شده در محیط پروژه و مبنای پشتیبانی نسخه فعلی |
| `BEST_EFFORT` | ممکن است با تغییرات Provider، Login یا Region از کار بیفتد |
| `METADATA_ONLY` | Metadata، Cover و لینک رسمی؛ نه Full Playback |
| `EXPERIMENTAL` | فقط برای تست، بدون تضمین Production |
| `DISABLED` | به دلیل Policy، ریسک یا خرابی موقت فعال نیست |

### 0.4 منابع مرجع Policy

- Telegram Bot API: https://core.telegram.org/bots/api
- Telegram Mini Apps: https://core.telegram.org/bots/webapps
- YouTube Developer Policies: https://developers.google.com/youtube/terms/developer-policies
- YouTube Terms: https://www.youtube.com/t/terms
- Spotify Web Playback SDK: https://developer.spotify.com/documentation/web-playback-sdk
- Spotify Track API: https://developer.spotify.com/documentation/web-api/reference/get-track

---

## 1) قوانین اجرایی برای هر AI یا Developer

این بخش الزام‌آور است و نباید با حدس یا سرعت بیشتر نادیده گرفته شود.

- قبل از تغییر: وضعیت Git، فایل‌ها، Playbook و تست‌های موجود را بخوان.
- هیچ Secret در Repository، Log، Chat، Screenshot یا Fixture قرار نده.
- `.env` فقط محلی/سرور و خارج از Git است؛ `.env.example` بدون مقدار واقعی Commit می‌شود.
- هر مرحله Gate دارد؛ بدون شرط خروج مرحله، به مرحله بعد نرو.
- تست اجرا نشده، تست موفق محسوب نمی‌شود.
- اگر یک Provider، Engine یا قابلیت تست نشده است، آن را `UNVERIFIED` اعلام کن.
- تغییر معماری بزرگ بدون ADR، تست و دلیل ثبت‌شده ممنوع است.
- دستورات مخرب، حذف گسترده، Force Push و تغییر Branch ممنوع است.
- برای Credential فقط دستورالعمل امن محلی بده؛ هیچ‌وقت Token یا کد ورود را از کاربر در چت نخواه.
- برای محتوای رسانه‌ای، فقط مسیرهای مجاز و محتوای دارای حق استفاده را پشتیبانی کن.
- همه خطاهای بیرونی باید قابل توضیح، قابل Retry یا قابل گزارش باشند؛ Crash خام قابل قبول نیست.
- بعد از هر مرحله، Changelog و وضعیت Gate به‌روزرسانی شود.

---

## 2) مسئولیت‌ها

### کاربر باید انجام دهد

- ساخت Bot با BotFather و نگه‌داری امن `BOT_TOKEN`.
- دریافت `API_ID` و `API_HASH` از `my.telegram.org`.
- داشتن یک Assistant User Account جداگانه برای Voice Chat.
- اجرای Session Generator روی سیستم امن خودش.
- ساخت یک Test Group و فعال‌کردن Voice Chat.
- افزودن Bot و Assistant به Test Group و دادن Permission لازم.
- تصمیم درباره Providerهای مجاز، حداکثر مدت و Policy محتوایی.
- فراهم‌کردن VPS، Domain و HTTPS فقط در مرحله Production.
- هرگز ارسال Credential در Chat یا Issue عمومی.

### Agent/Developer باید انجام دهد

- بررسی Repository و حفظ Branch/تاریخچه.
- ساخت معماری و کد مرحله‌ای.
- ساخت Session Generator محلی بدون ذخیره Credential در Log.
- نوشتن تست، Migration، مستندات و `.env.example`.
- اجرای تست واقعی و گزارش نتیجه، بدون ادعای کاذب.
- پیاده‌سازی Core مستقل از Telegram.
- پیاده‌سازی Adapterهای Provider با سطح پشتیبانی شفاف.
- ساخت پنل Native و Mini App طبق Gateهای پروژه.
- ثبت ریسک، Blocker و تصمیم‌های معماری.

---

## 3) معماری نهایی که باید حفظ شود

```text
Platform Adapters
      ↓
Command Gateway
      ↓
Application Use Cases
      ↓
Domain Core
      ↓
Ports
      ├── Queue/Playlist Repositories
      ├── Media Resolver
      ├── Playback Engine
      ├── Notification Renderer
      └── Permission Service
```

### اجزای Deployable

```text
bot-gateway       دریافت Command و Callback
player-service    Assistant، Voice Chat و Playback
media-worker      Resolve، Metadata، FFmpeg و Cleanup
webapp-api        Mini App و API خصوصی
postgres          منبع اصلی داده دائمی
redis             Lock، Cache و State موقت
```

در شروع می‌توان اجزای Python را در یک Process اجرا کرد، اما مرز Moduleها باید از ابتدا جدا باشد. Player و FFmpeg نباید مستقیماً داخل Handler تلگرام اجرا شوند.

### قوانین State

- PostgreSQL منبع اصلی Queue، Playlist، Permission و History است.
- Redis فقط برای Lock، Cache و State موقت است.
- هر گروه یک `ChatPlaybackActor` و یک Single Writer دارد.
- هر Command دارای `command_id` و Idempotency است.
- State Machine رسمی:

```text
IDLE → RESOLVING → BUFFERING → JOINING_CALL → PLAYING
PLAYING ↔ PAUSED
PLAYING/PAUSED → STOPPING → IDLE
هر State → ERROR با Recovery مشخص
```

---

# 4) مسیر کمینه اما کامل اجرا

## Gate 0 — حاکمیت پروژه و Baseline

### کارهای Agent

- [x] بررسی Repository و Remote.
- [x] ساخت `AGENTS.md`.
- [x] ساخت این Playbook.
- [ ] ثبت Branch جاری و قوانین Push در گزارش اجرای مرحله.
- [ ] ساخت/تکمیل README با لینک این سند.
- [ ] تعیین Python، FFmpeg و نسخه‌های Pin شده بعد از POC.
- [ ] اضافه‌کردن قالب Changelog و ADR.

### معیار خروج

- هر AI جدید بداند اول چه بخواند و چه چیزی ممنوع است.
- هیچ تصمیم فنی بدون Gate بعدی قفل نشود.

**وضعیت:** `DONE` برای Baseline؛ `GATE_1_BLOCKED_RUNTIME_PREREQUISITES` برای ادامه

---

## Gate 1 — ورودی امن و Playback Proof of Concept

این مهم‌ترین Gate است. قبل از ساخت UI، Providerهای زیاد یا Playlist باید انجام شود.

### کاربر باید انجام دهد

- [ ] Bot Token را محلی در `.env` قرار دهد.
- [ ] `API_ID` و `API_HASH` را محلی قرار دهد.
- [ ] Assistant User Account آماده کند.
- [ ] Session Generator را محلی اجرا کند.
- [ ] `ASSISTANT_SESSION` را فقط در `.env` قرار دهد.
- [ ] Test Group بسازد.
- [ ] Voice Chat را فعال کند.
- [ ] Bot و Assistant را وارد گروه کند.
- [ ] Permission لازم برای مدیریت/صحبت در Call را بدهد.

### Agent باید انجام دهد

- [ ] `pyproject.toml` و Python Environment.
- [ ] `.env.example` بدون Secret.
- [ ] Settings Validation.
- [ ] Session Generator محلی.
- [ ] Health Check برای Bot و Assistant.
- [ ] اتصال به Test Group.
- [ ] تست Tone.
- [ ] تست MP3.
- [ ] تست Pause/Resume/Skip/Leave.
- [ ] تست Reconnect.
- [ ] تست Video جداگانه.
- [ ] ثبت CPU، RAM، زمان Join و خطاها.

### معیار خروج Audio

همه موارد زیر باید در Test Group واقعی موفق شوند:

```text
Login → Join → Play → Pause → Resume → Skip → Leave → Reconnect
```

### معیار خروج Video

Video فقط وقتی `SUPPORTED` شود که:

- یک فایل معتبر پخش شود.
- Stop و Reconnect کار کند.
- Resource Usage ثبت شود.
- حداقل روی محیط تست مشخص‌شده بررسی شود.

در غیر این صورت Video با وضعیت `EXPERIMENTAL` باقی می‌ماند.

**وضعیت فعلی:** `BLOCKED_USER_INPUT`

---

## Gate 2 — Foundation و Core مستقل

### Agent باید انجام دهد

- [ ] ساخت ساختار `src/domain`، `src/application`، `src/infrastructure` و `src/adapters`.
- [ ] تعریف Entityهای `Track`، `QueueItem`، `Playlist`، `PlaybackSession`، `User` و `Chat`.
- [ ] تعریف Portهای `PlaybackPort`، `MediaResolverPort` و Repositoryها.
- [ ] ساخت SQLAlchemy Models.
- [ ] ساخت Alembic Migration اولیه.
- [ ] راه‌اندازی PostgreSQL و Redis با Docker Compose.
- [ ] ساخت Fake Playback Engine برای تست Core بدون Telegram.
- [ ] پیاده‌سازی Queue Rules.
- [ ] پیاده‌سازی State Machine.
- [ ] پیاده‌سازی Command Idempotency.
- [ ] نوشتن Unit Test.
- [ ] تنظیم Linter، Formatter و Type Check.

### معیار خروج

- Core بدون اتصال Telegram تست شود.
- Queue در تست‌های همزمان خراب نشود.
- Skip، Loop، Shuffle و Remove رفتار مشخص داشته باشند.
- Migration از دیتابیس خالی اجرا شود.

---

## Gate 3 — Telegram Audio MVP

### Agent باید انجام دهد

- [ ] `/play`.
- [ ] متن فارسی `پخش` در صورت دریافت Message.
- [ ] Reply روی فایل Audio/Video تلگرام.
- [ ] پخش Telegram File.
- [ ] پخش URL مستقیم مجاز.
- [ ] `/pause`، `/resume`، `/skip`، `/stop`.
- [ ] `/queue` و `/now`.
- [ ] `/volume` در صورت پشتیبانی Engine.
- [ ] Auto Join.
- [ ] Auto Leave.
- [ ] یک Queue مستقل برای هر Group.
- [ ] خطای واضح برای Call فعال‌نشده یا Permission ناقص.
- [ ] Native Now Playing Panel.
- [ ] Cover از منبع یا Cover Fallback.

### معیار خروج

- دو گروه جداگانه هم‌زمان Queue مستقل داشته باشند.
- Handlerهای Telegram مستقیماً FFmpeg را کنترل نکنند.
- خطای یک گروه، گروه دیگر را متوقف نکند.
- پیام‌های اضافی تولید نشود.

---

## Gate 4 — Persistence، امنیت و محصول اصلی

### Agent باید انجام دهد

- [ ] Playlist شخصی.
- [ ] Playlist گروهی.
- [ ] Favorites.
- [ ] History.
- [ ] Save Track.
- [ ] Permissionهای User/DJ/Admin/Owner.
- [ ] تنظیمات Group.
- [ ] Max Queue Size.
- [ ] Max Track Duration.
- [ ] Rate Limit.
- [ ] SSRF Protection.
- [ ] FFmpeg Timeout و Cleanup.
- [ ] Audit Log.
- [ ] `/delete_my_data`.
- [ ] Restart Recovery.
- [ ] Re-resolve برای URL منقضی.
- [ ] عدم چاپ Secret در Log.
- [ ] تست Backup و Restore دیتابیس.

### معیار خروج

- Restart باعث نابودی Queue نشود.
- عملیات هم‌زمان State را خراب نکند.
- یک کاربر نتواند Permission را دور بزند.
- فایل موقت بعد از پایان یا خطا پاک شود.
- کاربر بتواند داده‌های شخصی خود را حذف کند.

---

## Gate 5 — Provider System

### ترتیب اجرا

1. [ ] Telegram Provider — `GUARANTEED`
2. [ ] Direct URL Provider — `GUARANTEED` فقط برای منابع مجاز
3. [ ] SoundCloud — ابتدا `BEST_EFFORT`
4. [ ] YouTube Metadata/Search
5. [ ] YouTube Playback فقط با Policy صریح و تست مستقل
6. [ ] YouTube Music
7. [ ] Vimeo
8. [ ] Instagram Public
9. [ ] Twitch
10. [ ] TikTok
11. [ ] Spotify Metadata — `METADATA_ONLY`

### هر Provider باید داشته باشد

- [ ] URL Detection.
- [ ] Search در صورت امکان.
- [ ] Metadata.
- [ ] Thumbnail.
- [ ] Duration.
- [ ] Capability Matrix.
- [ ] Timeout.
- [ ] Retry محدود با Backoff.
- [ ] خطای استاندارد.
- [ ] Test Fixture یا Contract Test.
- [ ] Feature Flag.
- [ ] سطح پشتیبانی در مستندات.

### ممنوع

- [ ] دورزدن DRM.
- [ ] دورزدن Login یا Paywall.
- [ ] استفاده از Credential کاربر در Repository.
- [ ] ادعای پشتیبانی دائمی بدون تست.
- [ ] ذخیره دائمی غیرضروری محتوای شخص ثالث.

### معیار خروج

Provider خراب نباید کل Bot یا Player را Crash کند.

---

## Gate 6 — Video و Mini App

### Video

فقط اگر Gate 1 موفق شده باشد:

- [ ] Video File.
- [ ] Video URL مجاز.
- [ ] Audio/Video Mode.
- [ ] Resolution Limit.
- [ ] Bitrate Limit.
- [ ] Video Duration Limit.
- [ ] Stop Video.
- [ ] Reconnect.
- [ ] Resource Manager.
- [ ] تست CPU/RAM.

### Mini App

- [ ] HTTPS.
- [ ] اعتبارسنجی `initData`.
- [ ] Authorization بر اساس User و Chat.
- [ ] Dashboard.
- [ ] Queue Drag & Drop.
- [ ] Playlist Manager.
- [ ] Search.
- [ ] وضعیت Now Playing.
- [ ] WebSocket با احراز هویت.
- [ ] RTL و Theme تلگرام.
- [ ] Fallback به Native Panel.

### معیار خروج

Mini App نباید قابلیت‌های اصلی Bot را خراب کند. هر قابلیت باید از همان Application Use Case استفاده کند، نه منطق جداگانه.

---

## Gate 7 — Production و Release

### Agent باید انجام دهد

- [ ] Dockerfile Production.
- [ ] Docker Compose Production.
- [ ] Reverse Proxy و HTTPS.
- [ ] Health Endpoint.
- [ ] Readiness/Liveness Check.
- [ ] Structured Logging.
- [ ] Metrics.
- [ ] Alerting.
- [ ] Database Backup.
- [ ] Restore Drill.
- [ ] Graceful Shutdown.
- [ ] Retry و Backoff.
- [ ] Resource Quota.
- [ ] Runbook خطاها.
- [ ] مستندات نصب از صفر.
- [ ] تست Clean Install.
- [ ] Security Review.
- [ ] `git diff --check`.
- [ ] حذف Secretهای احتمالی با بررسی Git.
- [ ] Tag نسخه فقط بعد از قبولی همه Gateها.

### کاربر باید انجام دهد

- [ ] VPS مناسب فراهم کند.
- [ ] Domain و HTTPS فراهم کند.
- [ ] `.env` Production را خارج از Git ایجاد کند.
- [ ] Backup Location تعیین کند.
- [ ] Test Group و Admin نهایی تعیین کند.
- [ ] Policy استفاده از محتوا را تأیید کند.
- [ ] تست پذیرش نهایی را انجام دهد.

### معیار Release

```text
All mandatory tests pass
No secrets in Git
Audio POC passed
Recovery passed
Backup restored successfully
Provider levels documented
Known limitations published
User setup documented
```

---

# 5) ساختار پیشنهادی Repository

```text
music-player-bot/
├── AGENTS.md
├── README.md
├── CHANGELOG.md
├── ADR/
├── docs/
│   ├── PROJECT_PLAYBOOK.md
│   ├── ARCHITECTURE.md
│   ├── OPERATIONS.md
│   ├── PROVIDERS.md
│   └── SECURITY.md
├── src/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   └── adapters/
├── web/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   └── live/
├── migrations/
├── docker/
├── scripts/
├── .env.example
├── .gitignore
├── docker-compose.yml
└── pyproject.toml
```

---

# 6) Definition of Done عمومی

یک Feature فقط وقتی Done است که:

- [ ] Domain/Application منطق اصلی را دارد.
- [ ] Adapter فقط تبدیل ورودی و خروجی انجام می‌دهد.
- [ ] Permission بررسی می‌شود.
- [ ] خطاهای مورد انتظار مدیریت می‌شوند.
- [ ] Unit Test نوشته شده است.
- [ ] Integration Test در صورت نیاز نوشته شده است.
- [ ] Log امن و قابل جستجو وجود دارد.
- [ ] Migration در صورت تغییر دیتابیس وجود دارد.
- [ ] `.env.example` به‌روز است.
- [ ] مستندات تغییر کرده‌اند.
- [ ] تست واقعاً اجرا شده است.
- [ ] محدودیت Feature مستند شده است.

---

# 7) گزارش پایان هر مرحله

Agent باید در پایان هر مرحله این قالب را تکمیل کند:

```text
Stage:
Status: DONE | READY | BLOCKED | FAILED
Changes:
Tests executed:
Tests not executed:
User actions required:
Known risks:
Provider/Policy impact:
Next stage:
Commit:
```

هیچ مرحله‌ای که `BLOCKED` یا `FAILED` است نباید به‌عنوان موفق گزارش شود.

---

# 8) وضعیت فعلی پروژه

```text
Gate 0 — Playbook و قوانین: DONE
Gate 1 — Credential و Playback POC: BLOCKED_USER_INPUT
Gate 2 — Foundation: NOT_STARTED
Gate 3 — Audio MVP: NOT_STARTED
Gate 4 — Persistence/Security/Product: NOT_STARTED
Gate 5 — Providers: NOT_STARTED
Gate 6 — Video/Mini App: NOT_STARTED
Gate 7 — Production/Release: NOT_STARTED
```

## اولین اقدام بعدی

کاربر باید ورودی‌های Gate 1 را روی سیستم امن خودش آماده کند. سپس Agent ابتدا Playback POC را می‌سازد و اجرا می‌کند؛ نه اینکه مستقیم سراغ ساخت همه Providerها و پنل‌ها برود.
