#!/bin/bash
# ================================================================
# 节假日数据同步测试脚本
# ================================================================
# 用途：在服务器上快速测试节假日数据同步功能
# 使用：bash test_holiday_sync.sh
# ================================================================

echo "============================================================"
echo "🧪 节假日数据同步功能测试"
echo "============================================================"
echo ""

# 切换到 backend 目录
cd ~/kotlin_calendar/backend

# ============================================================
# 测试 1：导入 2024-2027 年节假日数据
# ============================================================
echo "📦 测试 1：导入 2024-2027 年节假日数据"
echo "------------------------------------------------------------"
python3 manage.py import_holidays --start-year 2024 --end-year 2027
echo ""

# ============================================================
# 测试 2：查看数据库中的节假日数量
# ============================================================
echo "📊 测试 2：查看数据库中的节假日数量"
echo "------------------------------------------------------------"
python3 manage.py shell << EOF
from api.models import Holiday
from datetime import date

# 总数
total = Holiday.objects.count()
print(f"✓ 数据库中共有 {total} 条节假日记录")

# 按年份统计
current_year = date.today().year
for year in range(2024, 2028):
    count = Holiday.objects.filter(date__year=year).count()
    status = "✓" if count > 0 else "✗"
    print(f"  {status} {year} 年: {count} 条")

EOF
echo ""

# ============================================================
# 测试 3：查询指定日期的节假日
# ============================================================
echo "🔍 测试 3：查询指定日期的节假日"
echo "------------------------------------------------------------"
python3 manage.py shell << EOF
from api.models import Holiday
from datetime import date

test_dates = [
    date(2025, 1, 1),   # 元旦
    date(2025, 1, 28),  # 春节
    date(2025, 10, 1),  # 国庆
]

for d in test_dates:
    holiday = Holiday.objects.filter(date=d).first()
    if holiday:
        print(f"  ✓ {d} - {holiday.name} {holiday.emoji}")
    else:
        print(f"  ✗ {d} - 无数据")

EOF
echo ""

# ============================================================
# 测试 4：测试 API 接口
# ============================================================
echo "🌐 测试 4：测试 API 接口"
echo "------------------------------------------------------------"

echo "  > 测试：查询 2025 年节假日列表"
curl -s "https://app7626.acapp.acwing.com.cn/api/v1/holidays/?year=2025" | python3 -m json.tool | head -20
echo ""

echo "  > 测试：检查 2025-01-01 是否是节假日"
curl -s "https://app7626.acapp.acwing.com.cn/api/v1/holidays/check/?date=2025-01-01" | python3 -m json.tool
echo ""

echo "  > 测试：查询今日节假日"
curl -s "https://app7626.acapp.acwing.com.cn/api/v1/holidays/today/" | python3 -m json.tool
echo ""

# ============================================================
# 测试 5：查看同步日志
# ============================================================
echo "📋 测试 5：查看同步日志"
echo "------------------------------------------------------------"
python3 manage.py shell << EOF
from api.models import DataSyncLog

logs = DataSyncLog.objects.filter(data_type='holiday').order_by('-created_at')[:5]
if logs.exists():
    print(f"  ✓ 最近 {logs.count()} 条同步日志：")
    for log in logs:
        status_icon = "✓" if log.status == "success" else "✗"
        date_range = f"{log.sync_date}"
        if log.sync_date_end:
            date_range += f" ~ {log.sync_date_end}"
        print(f"    {status_icon} {log.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {date_range} - {log.records_count}条")
else:
    print("  ✗ 暂无同步日志")

EOF
echo ""

# ============================================================
# 完成
# ============================================================
echo "============================================================"
echo "✅ 测试完成！"
echo "============================================================"
echo ""
echo "📚 使用说明："
echo "  - 导入指定年份：python3 manage.py import_holidays --year 2025"
echo "  - 批量导入：python3 manage.py import_holidays --start-year 2024 --end-year 2027"
echo "  - 强制更新：python3 manage.py import_holidays --replace"
echo ""
echo "📖 详细文档：docs/features/HOLIDAY_SYNC_GUIDE.md"
echo ""

