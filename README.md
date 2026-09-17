# Music Player Bot

پلتفرم ماژولار پخش موسیقی و ویدیو برای Telegram Voice Chat با هسته قابل توسعه برای پلتفرم‌های آینده.

## مهم

این پروژه به دو هویت تلگرام نیاز دارد:

- Bot Account برای Command، پنل و مدیریت
- Assistant User Account برای ورود به Voice Chat و پخش رسانه

هیچ Token، API Hash یا `STRING_SESSION` را در Git یا Chat قرار ندهید.

## شروع سریع

روی Ubuntu/Debian می‌توانید Setup تعاملی را اجرا کنید؛ این ابزار Python، FFmpeg، محیط مجازی، Dependencyها، `.env`، پورت‌های جدا و Assistant Session را مرحله‌به‌مرحله تنظیم می‌کند:

```bash
bash scripts/setup.sh
```

اگر این فایل وجود ندارد، ابتدا روی Branch پروژه قرار بگیرید:

```bash
git fetch origin arena/01a0af03-music-player-bot
git switch arena/01a0af03-music-player-bot || git switch --track origin/arena/01a0af03-music-player-bot
git pull --ff-only origin arena/01a0af03-music-player-bot
```

برای راهنمای کامل Credential و Providerها:

قبل از هر تغییر کد، این سند را بخوانید:

- [AGENTS.md](AGENTS.md)
- [Project Playbook](docs/PROJECT_PLAYBOOK.md)
- [راهنمای تکمیل `.env` و راه‌اندازی Providerها](docs/SETUP_ENV.md)

Playbook شامل معماری، مراحل Gate-based، مسئولیت کاربر و Agent، معیارهای تست، محدودیت Providerها و قواعد امنیتی پروژه است. راهنمای Setup نیز تفاوت PostgreSQL روی پورت 5431، Docker، Telegram، Assistant، FFmpeg، YouTube و Spotify را توضیح می‌دهد.

## وضعیت فعلی

مستندات و قرارداد اجرایی آماده شده‌اند. مرحله بعدی، آماده‌سازی امن Credentialها و اجرای Playback Proof of Concept است.
