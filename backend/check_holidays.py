"""
检查节日数据脚本
用于诊断节日信息丢失问题
"""
import os
import sys
import django
import json
from datetime import datetime

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'calendar_backend.settings')
django.setup()

from api.models import Holiday
from django.core.cache import cache

def check_holidays():
    """检查节日数据"""
    print("=" * 60)
    print("节日数据检查")
    print("=" * 60)
    print()
    
    current_year = datetime.now().year
    
    # 1. 检查数据库中的节日数据
    print("1. 检查数据库中的节日数据:")
    print("-" * 60)
    
    holidays_in_db = Holiday.objects.all()
    print(f"   总记录数: {holidays_in_db.count()}")
    
    if holidays_in_db.exists():
        # 按年份统计
        years = {}
        for holiday in holidays_in_db:
            year = holiday.date.year
            if year not in years:
                years[year] = []
            years[year].append(holiday)
        
        print(f"   覆盖年份: {sorted(years.keys())}")
        for year in sorted(years.keys()):
            print(f"     {year}年: {len(years[year])} 条记录")
        
        # 显示当前年份的节日
        current_year_holidays = [h for h in holidays_in_db if h.date.year == current_year]
        if current_year_holidays:
            print(f"\n   当前年份 ({current_year}) 的节日示例（前5个）:")
            for holiday in sorted(current_year_holidays, key=lambda x: x.date)[:5]:
                print(f"     {holiday.date} - {holiday.name} ({holiday.type})")
    else:
        print("   ❌ 数据库中没有节日数据！")
    
    print()
    
    # 2. 检查JSON文件
    print("2. 检查JSON文件:")
    print("-" * 60)
    
    data_dir = os.path.join(os.path.dirname(__file__), 'api', 'data')
    json_file = os.path.join(data_dir, f'holidays_{current_year}.json')
    
    if os.path.exists(json_file):
        print(f"   ✅ JSON文件存在: {json_file}")
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                holidays_json = json.load(f)
            
            if str(current_year) in holidays_json:
                year_data = holidays_json[str(current_year)]
                print(f"   ✅ 找到 {current_year} 年的数据")
                print(f"   节日数量: {len(year_data)}")
                
                # 显示前5个节日
                print(f"\n   节日示例（前5个）:")
                for i, (name, date) in enumerate(list(year_data.items())[:5]):
                    print(f"     {name}: {date}")
            else:
                print(f"   ⚠️  JSON文件中没有 {current_year} 年的数据")
        except Exception as e:
            print(f"   ❌ 读取JSON文件失败: {str(e)}")
    else:
        print(f"   ❌ JSON文件不存在: {json_file}")
    
    print()
    
    # 3. 检查缓存
    print("3. 检查缓存:")
    print("-" * 60)
    
    cache_key = f'holidays_{current_year}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        print(f"   ✅ 缓存中有数据 (key: {cache_key})")
        if str(current_year) in cached_data:
            year_data = cached_data[str(current_year)]
            print(f"   节日数量: {len(year_data)}")
    else:
        print(f"   ⚠️  缓存中没有数据 (key: {cache_key})")
    
    print()
    
    # 4. 建议
    print("4. 建议:")
    print("-" * 60)
    
    if not holidays_in_db.exists():
        print("   ❌ 数据库中没有节日数据，建议执行:")
        print("      python3 manage.py import_holidays")
    elif current_year not in [h.date.year for h in holidays_in_db]:
        print(f"   ⚠️  数据库中没有 {current_year} 年的数据，建议执行:")
        print(f"      python3 manage.py import_holidays --year {current_year}")
    else:
        print("   ✅ 数据库中有节日数据")
    
    if not os.path.exists(json_file):
        print("   ⚠️  JSON文件不存在，但这不是必需的（数据库优先）")
    
    print()

if __name__ == '__main__':
    check_holidays()

