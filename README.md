# TUI Tracker

این پروژه هر روز صفحه جستجوی TUI را با GitHub Actions باز می‌کند و قیمت‌های سفر به Zakynthos را بررسی می‌کند.

## تنظیمات فعلی

- مبدأ: Göteborg Landvetter
- مقصد: Zakynthos
- تاریخ خروج: 4 تا 8 سپتامبر 2026
- تعداد مسافران: 2 نفر
- سقف قیمت: 25,000 SEK
- اجرای روزانه: 07:00 UTC

## Secrets لازم

در GitHub برو به:

`Settings → Secrets and variables → Actions`

سه Secret بساز:

- `EMAIL_USER`: آدرس Gmail فرستنده
- `EMAIL_PASSWORD`: App Password شانزده‌رقمی Gmail
- `EMAIL_TO`: ایمیلی که هشدار باید به آن ارسال شود

## اجرای دستی

`Actions → TUI Tracker → Run workflow`

## بررسی خطا

بعد از هر اجرا یک Artifact به نام `tui-debug` ساخته می‌شود که شامل این‌هاست:

- `debug_page_text.txt`
- `debug_screenshot.png`

اگر سایت TUI نتیجه‌ها را تغییر دهد، این دو فایل برای پیدا کردن مشکل استفاده می‌شوند.

## نکته

TUI ممکن است ساختار صفحه، متن یا روش نمایش قیمت‌ها را تغییر دهد. این نسخه با استخراج عمومی قیمت‌ها کار می‌کند و در صورت تغییر سایت ممکن است نیاز به تنظیم Selectorها داشته باشد.
