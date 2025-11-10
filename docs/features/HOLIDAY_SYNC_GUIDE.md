# 📅 节假日数据自动同步功能指南

## 📖 功能概述

Ralendar 现在支持**自动同步中国法定节假日数据**，无需手动维护，确保节假日信息始终准确最新！

### ✨ 核心特性

- ✅ **自动同步**：每月1号自动从 Timor API 获取最新数据
- ✅ **多年覆盖**：默认同步去年、今年、未来2年（共4年）
- ✅ **手动导入**：支持命令行手动导入指定年份
- ✅ **数据替换**：自动更新已存在的数据，确保最新
- ✅ **日志记录**：完整的同步日志，方便追踪

---

## 🚀 快速开始

### 1. 首次导入数据

在服务器上执行以下命令：

```bash
cd ~/kotlin_calendar/backend

# 导入默认年份（2024-2027）
python3 manage.py import_holidays
```

**预期输出：**
```
============================================================
🚀 开始批量同步节假日数据 (2024 - 2027)
============================================================

🔄 开始同步 2024 年节假日数据...
✓ 成功获取 365 天的数据
✓ 解析出 29 条节假日记录
  ✓ 新增: 2024-01-01 - 元旦
  ✓ 新增: 2024-02-10 - 春节
  ...
  
📊 导入统计:
  - 成功: 29 条
  - 跳过: 0 条

✅ 2024 年节假日数据同步完成！

============================================================
✅ 批量同步完成！
  - 成功: 4 年
  - 失败: 0 年
============================================================
```

---

## 📚 使用方法

### 方法 1：Django 管理命令（推荐）

#### A. 导入默认年份（去年、今年、未来2年）

```bash
python3 manage.py import_holidays
```

#### B. 导入指定年份

```bash
# 导入 2025 年
python3 manage.py import_holidays --year 2025

# 导入 2026 年
python3 manage.py import_holidays --year 2026
```

#### C. 批量导入年份范围

```bash
# 导入 2024-2027 年
python3 manage.py import_holidays --start-year 2024 --end-year 2027

# 导入 2020-2030 年（大范围）
python3 manage.py import_holidays --start-year 2020 --end-year 2030
```

#### D. 强制替换已存在的数据

```bash
# 替换已存在的数据（适用于数据更新）
python3 manage.py import_holidays --replace

# 导入指定年份并替换
python3 manage.py import_holidays --year 2025 --replace
```

---

### 方法 2：Celery 定时任务（自动）

Celery Beat 已配置为**每月1号凌晨3点**自动同步节假日数据。

#### 查看定时任务配置

```bash
cd ~/kotlin_calendar/backend
python3 manage.py shell
```

```python
from celery import current_app

# 查看所有定时任务
for task_name, task_config in current_app.conf.beat_schedule.items():
    print(f"{task_name}: {task_config}")

# 输出：
# sync-holiday-data: {
#     'task': 'api.tasks.sync_holiday_data',
#     'schedule': crontab(hour=3, minute=0, day_of_month=1)
# }
```

#### 手动触发定时任务（测试）

```python
from api.tasks import sync_holiday_data

# 立即执行
result = sync_holiday_data.delay()
print(result.get())
```

---

### 方法 3：Python 代码调用

在 Django shell 或代码中直接调用：

```python
from api.utils.holiday_sync import HolidaySyncService, sync_holidays

# 方式 1：使用便捷函数
sync_holidays(year=2025)  # 同步单个年份
sync_holidays()  # 同步默认年份（去年、今年、未来2年）

# 方式 2：使用服务类
service = HolidaySyncService()

# 同步单个年份
service.sync_year_holidays(2025, replace=True)

# 批量同步
service.sync_multiple_years(2024, 2027, replace=True)

# 查询指定日期
from datetime import date
info = service.fetch_date_holiday_from_timor(date(2025, 1, 1))
print(info)  # {'type': 2, 'name': '元旦', 'week': 3}
```

---

## 🔧 配置说明

### 数据来源

**Timor API**：http://timor.tech/api/holiday

- ✅ **免费使用**：无需注册
- ✅ **国内可访问**：速度快
- ✅ **数据准确**：基于国务院公告
- ✅ **自动更新**：维护者会及时更新

### 数据范围

默认同步：**去年、今年、未来2年**（共4年）

例如，当前是 2025 年：
- 2024 年（去年）
- 2025 年（今年）
- 2026 年（明年）
- 2027 年（后年）

### 定时任务

**执行时间**：每月1号凌晨3点

**执行策略**：
- 自动同步4年数据
- 自动替换已存在的数据
- 记录同步日志

---

## 📊 数据查看

### 1. 查看数据库中的节假日

```bash
cd ~/kotlin_calendar/backend
python3 manage.py shell
```

```python
from api.models import Holiday
from datetime import date

# 查看总数
count = Holiday.objects.count()
print(f"共有 {count} 条节假日记录")

# 查看 2025 年的节假日
holidays_2025 = Holiday.objects.filter(date__year=2025)
for h in holidays_2025:
    print(f"{h.date} - {h.name} ({h.emoji})")

# 查询指定日期
holiday = Holiday.objects.filter(date=date(2025, 1, 1)).first()
if holiday:
    print(f"元旦：{holiday.name}, 法定假日：{holiday.is_legal_holiday}")
```

### 2. 通过 API 查询

```bash
# 查看所有年份
curl https://app7626.acapp.acwing.com.cn/api/v1/holidays/?year=2025

# 检查指定日期
curl "https://app7626.acapp.acwing.com.cn/api/v1/holidays/check/?date=2025-01-01"

# 查看今天
curl https://app7626.acapp.acwing.com.cn/api/v1/holidays/today/
```

### 3. 查看同步日志

```python
from api.models import DataSyncLog

# 查看最近10条同步日志
logs = DataSyncLog.objects.filter(data_type='holiday').order_by('-created_at')[:10]
for log in logs:
    date_range = f"{log.sync_date}"
    if log.sync_date_end:
        date_range += f" ~ {log.sync_date_end}"
    print(f"{log.created_at} - {log.status}: {date_range} - {log.records_count}条")
```

---

## 🐛 故障排查

### 问题 1：网络连接失败

**症状**：
```
❌ 网络请求失败: HTTPConnectionPool(host='timor.tech', port=80)
```

**解决方案**：
1. 检查服务器网络连接
2. 尝试手动访问：`curl http://timor.tech/api/holiday/year/2025`
3. 如果持续失败，考虑使用其他数据源

### 问题 2：数据已存在但需要更新

**症状**：
```
- 跳过: 2025-01-01 - 元旦 (已存在)
```

**解决方案**：
使用 `--replace` 参数强制更新：
```bash
python3 manage.py import_holidays --year 2025 --replace
```

### 问题 3：Celery 定时任务未执行

**检查步骤**：

```bash
# 1. 检查 Celery Beat 是否运行
ps aux | grep celery

# 2. 查看 Beat 日志
tail -50 ~/kotlin_calendar/backend/logs/celery_beat.log

# 3. 查看 Worker 日志
tail -50 ~/kotlin_calendar/backend/logs/celery_worker.log

# 4. 重启 Celery
pkill -f "celery.*calendar_backend"
cd ~/kotlin_calendar/backend
nohup python3 -m celery -A calendar_backend worker --concurrency=1 --loglevel=info > logs/celery_worker.log 2>&1 &
nohup python3 -m celery -A calendar_backend beat --loglevel=info > logs/celery_beat.log 2>&1 &
```

---

## 📅 维护建议

### 日常维护

1. **每月检查一次**：确保自动同步正常工作
2. **国务院公告后**：手动执行一次同步确保及时更新
3. **年底/年初**：确认新一年的数据已导入

### 检查命令

```bash
# 快速检查当前年份数据
cd ~/kotlin_calendar/backend
python3 manage.py shell -c "
from api.models import Holiday
from datetime import date
year = date.today().year
count = Holiday.objects.filter(date__year=year).count()
print(f'{year}年共有 {count} 条节假日记录')
"
```

### 手动更新流程

当国务院发布新的节假日安排时：

```bash
# 1. 备份现有数据（可选）
python3 manage.py dumpdata api.Holiday > holidays_backup.json

# 2. 重新导入数据
python3 manage.py import_holidays --year 2025 --replace

# 3. 验证数据
python3 manage.py shell -c "
from api.models import Holiday
holidays = Holiday.objects.filter(date__year=2025)
for h in holidays:
    print(f'{h.date} - {h.name}')
"
```

---

## 🎯 下一步扩展

- [ ] 支持更多数据源（APISpace、聚合数据等）
- [ ] 添加传统节日（七夕、重阳、腊八等）
- [ ] 添加国际节日（圣诞、情人节等）
- [ ] 用户自定义节日
- [ ] 节假日提醒功能

---

## 📞 技术支持

如有问题，请查看：
- 📖 API 文档：`docs/api/HOLIDAYS_API.md`
- 🗄️ 数据模型：`docs/database/CALENDAR_DATA_MODELS.md`
- 📝 开发日志：`docs/daily_logs/`

---

**✅ 功能已上线，祝使用愉快！** 🎉

