# دستورالعمل اجرای پروژه برای هر AI یا Coding Agent

> این فایل قرارداد اجرایی پروژه است. قبل از هر تغییر کد، ابتدا `docs/PROJECT_PLAYBOOK.md` را کامل بخوان.

## قواعد غیرقابل‌مذاکره

1. قبل از هر تغییر، `git status --short --branch`، ساختار پروژه و مستندات را بررسی کن.
2. بدون تکمیل Gate مربوطه به مرحله بعد نرو؛ اگر ورودی کاربر یا تست لازم وجود ندارد، وضعیت را `BLOCKED` ثبت کن و ادعای موفقیت نکن.
3. هیچ Secret، Token، API Hash، شماره تلفن، کد ورود یا `STRING_SESSION` را در چت، Git، Log، Screenshot یا تست Commit نکن.
4. فقط از `.env` محلی یا Secret Manager استفاده کن؛ فقط `.env.example` بدون مقدار حساس در Repository مجاز است.
5. هر تغییر باید تست، مستندات و دلیل تغییر داشته باشد. تست اجرا نشده را «موفق» اعلام نکن.
6. هرگز DRM، Login، Paywall، Geo Restriction، Rate Limit یا محدودیت فنی/حقوقی Providerها را دور نزن.
7. پشتیبانی Providerها را با سطح `GUARANTEED`، `BEST_EFFORT`، `METADATA_ONLY` یا `EXPERIMENTAL` اعلام کن؛ هیچ Provider خارجی را بدون تست پایدار قطعی معرفی نکن.
8. Bot Account را با Assistant User Account اشتباه نگیر. ورود به Voice Chat باید با Assistant انجام شود و Session آن فقط محلی تولید و نگه‌داری شود.
9. قبل از تغییر Schema، Migration بنویس. قبل از تغییر API یا Event، قرارداد و تست مربوطه را به‌روزرسانی کن.
10. هیچ‌وقت تاریخچه Git، `.git`، فایل‌های کاربر یا فایل‌های Credential را حذف، Rename یا پاک‌سازی مخرب نکن.
11. روی Branch فعلی کار کن؛ Branch جدید نساز و Branch را عوض نکن مگر مالک Repository صریحاً دستور داده باشد.
12. قبل از Commit، `git diff --check`، تست‌ها و `git status` را اجرا کن و خلاصه دقیق تغییرات را گزارش بده.
13. در پایان هر مرحله، وضعیت Gate، کارهای انجام‌شده، کارهای باقی‌مانده و Blockerها را ثبت کن.

## قرارداد خروجی هر مرحله

هر مرحله باید این موارد را تحویل دهد:

- تغییرات فایل‌ها
- تست‌های اجراشده و نتیجه واقعی
- دستور اجرای محلی
- متغیرهای `.env` لازم، بدون مقدار Secret
- محدودیت‌ها و ریسک‌های باقی‌مانده
- وضعیت Gate بعدی: `READY` یا `BLOCKED`

## ترتیب اجرا

```text
1. خواندن Playbook و بررسی Repository
2. دریافت ورودی‌های امن کاربر
3. Playback Proof of Concept
4. Foundation و Core مستقل
5. Audio MVP تلگرام
6. Persistence، امنیت و UX
7. Providerها به‌صورت جداگانه
8. Video فقط بعد از تست؛ رابط اصلی پروژه Telegram Native Panel است
9. Production Hardening و Release
```

## خط‌قرمز محصول

قابلیت Spotify Full Track در Telegram Voice Chat، دورزدن DRM/Paywall، پخش محتوای Private بدون مجوز و تضمین همیشگی سرویس‌های خارجی جزو وعده‌های محصول نیستند. جزئیات و معیارهای کامل در `docs/PROJECT_PLAYBOOK.md` ثبت شده است.
