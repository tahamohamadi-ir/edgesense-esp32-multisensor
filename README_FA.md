# راهنمای فارسی شروع EdgeSense

این مخزن یک چارچوب واقعی برای **برنامه‌نویسی و ارزیابی داده حسگر** است، اما فعلاً هیچ تست سخت‌افزاری انجام نشده. مخزن مستقل از ADaMS Lab است.

## فاز اول

۱. اول مدل PCB، سیم‌بندی، ولتاژهای ۳٫۳ ولت و I²C را با مولتی‌متر تأیید کن. پایه‌های دو ردیف برد ESP32 هنوز باید لحیم شوند.

۲. فقط ماژول MPU6050 را راه‌اندازی کن؛ بعد MLX90614 را اضافه کن؛ DS18B20 پس از شناسایی کابل/مقاومت Pull-up.

۳. از داخل `firmware/` پروفایل `edgesense` را با PlatformIO بساز؛ بعد از بررسی GPIOها Firmware را فلش کن.

۴. روی ویندوز:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[test,serial]"
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m edgesense.cli simulate --out data/synthetic/fixture.jsonl
.\.venv\Scripts\python.exe -m edgesense.cli audit --input data/synthetic/fixture.jsonl
# پس از راه‌اندازی واقعی، پورت COM خود را جایگزین کن:
.\.venv\Scripts\python.exe -m edgesense.cli capture --port COM5 --seconds 120 --out data/raw/run001.jsonl
.\.venv\Scripts\python.exe -m edgesense.cli audit --input data/raw/run001.jsonl --out reports/run001.json
```

## برنامه دوم — PPG + Motion

پروفایل `ppg_motion` با MAX30102 و MPU6050 است و به‌صورت مستقل فلش می‌شود. تا تأیید VIN و سطح منطقی ماژول MAX30102، به آن تغذیه نده. خروجی خام آن مجوز ادعای اندازه‌گیری پزشکی ضربان یا اشباع اکسیژن نیست. حسگر AD8232 در این پروژه استفاده نمی‌شود و **نباید با الکترودهای متصل به بدن، به تجهیزات USB غیرایزوله وصل شود**.

## GitHub و CV

تنها ادعای فعلاً مجاز: «implementation of a research prototype and quality-evaluation pipeline». بعد از تست واقعی می‌توان تعداد جلسات، نرخ نمونه‌برداری و درصد داده سالم را در README درج کرد. از `experiments/EVIDENCE_LOG_TEMPLATE.md` برای ثبت شواهد استفاده کن.
