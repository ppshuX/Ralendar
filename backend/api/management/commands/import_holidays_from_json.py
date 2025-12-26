"""
从JSON文件导入节假日数据到数据库

使用方法:
    python manage.py import_holidays_from_json
    python manage.py import_holidays_from_json --year 2025
"""
import os
import json
from datetime import datetime, date
from django.core.management.base import BaseCommand
from django.utils import timezone
from api.models import Holiday


class Command(BaseCommand):
    help = '从JSON文件导入节假日数据到数据库'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            help='指定要导入的年份（默认导入所有可用年份）'
        )
        parser.add_argument(
            '--replace',
            action='store_true',
            help='替换已存在的数据（默认跳过已存在的记录）'
        )
    
    def parse_json_to_holidays(self, year: int, year_data: dict) -> list:
        """
        将JSON格式的节假日数据转换为Holiday模型数据
        
        JSON格式:
        {
            "元旦": "2025-01-01",
            "春节": "2025-01-28",
            "春节假期": ["2025-01-28", "2025-01-29", ...],
            ...
        }
        """
        holidays = []
        
        for holiday_name, holiday_date in year_data.items():
            if isinstance(holiday_date, str):
                # 单个日期（主要节日）
                try:
                    holiday_date_obj = datetime.strptime(holiday_date, '%Y-%m-%d').date()
                    holidays.append({
                        'date': holiday_date_obj,
                        'name': holiday_name,
                        'type': 'major',
                        'is_legal_holiday': True,
                        'is_rest_day': True,
                        'is_workday': False,
                        'holiday_group': None,
                    })
                except ValueError:
                    self.stdout.write(self.style.WARNING(f"   ⚠️  跳过无效日期: {holiday_name} = {holiday_date}"))
            
            elif isinstance(holiday_date, list):
                # 假期日期范围
                holiday_group = holiday_name  # 使用假期名称作为组名
                for i, date_str in enumerate(holiday_date):
                    try:
                        holiday_date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                        
                        # 第一天是主要节日，其他天是假期
                        if i == 0:
                            holiday_type = 'major'
                            is_legal_holiday = True
                        else:
                            holiday_type = 'vacation'
                            is_legal_holiday = False
                        
                        holidays.append({
                            'date': holiday_date_obj,
                            'name': holiday_name.replace('假期', '') if '假期' in holiday_name else holiday_name,
                            'type': holiday_type,
                            'is_legal_holiday': is_legal_holiday,
                            'is_rest_day': True,
                            'is_workday': False,
                            'holiday_group': holiday_group,
                        })
                    except ValueError:
                        self.stdout.write(self.style.WARNING(f"   ⚠️  跳过无效日期: {date_str}"))
        
        return holidays
    
    def handle(self, *args, **options):
        year = options.get('year')
        replace = options.get('replace', False)
        
        # JSON文件路径
        data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
        
        if year:
            # 导入指定年份
            json_file = os.path.join(data_dir, f'holidays_{year}.json')
            
            if not os.path.exists(json_file):
                self.stdout.write(self.style.ERROR(f'❌ JSON文件不存在: {json_file}'))
                return
            
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(f"🎯 从JSON导入 {year} 年节假日数据")
            self.stdout.write(f"{'='*60}\n")
            
            self.import_year_from_json(json_file, year, replace)
        else:
            # 导入所有可用年份
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(f"🎯 从JSON导入所有可用年份的节假日数据")
            self.stdout.write(f"{'='*60}\n")
            
            # 查找所有holidays_*.json文件
            json_files = [f for f in os.listdir(data_dir) if f.startswith('holidays_') and f.endswith('.json')]
            
            if not json_files:
                self.stdout.write(self.style.ERROR(f'❌ 在 {data_dir} 中未找到节假日JSON文件'))
                return
            
            for json_file in sorted(json_files):
                # 从文件名提取年份
                try:
                    year = int(json_file.replace('holidays_', '').replace('.json', ''))
                    json_path = os.path.join(data_dir, json_file)
                    self.import_year_from_json(json_path, year, replace)
                except ValueError:
                    self.stdout.write(self.style.WARNING(f"   ⚠️  跳过无法解析年份的文件: {json_file}"))
        
        self.stdout.write('\n')
    
    def import_year_from_json(self, json_file: str, year: int, replace: bool):
        """从JSON文件导入指定年份的数据"""
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                holidays_json = json.load(f)
            
            if str(year) not in holidays_json:
                self.stdout.write(self.style.WARNING(f"   ⚠️  JSON文件中没有 {year} 年的数据"))
                return
            
            year_data = holidays_json[str(year)]
            holidays = self.parse_json_to_holidays(year, year_data)
            
            if not holidays:
                self.stdout.write(self.style.WARNING(f"   ⚠️  解析出 0 条节假日记录"))
                return
            
            self.stdout.write(f"   ✓ 解析出 {len(holidays)} 条节假日记录\n")
            
            # 导入到数据库
            imported_count = 0
            skipped_count = 0
            
            for holiday_data in holidays:
                try:
                    existing = Holiday.objects.filter(
                        date=holiday_data['date'],
                        name=holiday_data['name'],
                        type=holiday_data['type']
                    ).first()
                    
                    if existing:
                        if replace:
                            for key, value in holiday_data.items():
                                setattr(existing, key, value)
                            existing.save()
                            imported_count += 1
                            self.stdout.write(f"     ✓ 更新: {holiday_data['date']} - {holiday_data['name']}")
                        else:
                            skipped_count += 1
                    else:
                        Holiday.objects.create(**holiday_data)
                        imported_count += 1
                        self.stdout.write(f"     ✓ 新增: {holiday_data['date']} - {holiday_data['name']}")
                        
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"     ❌ 导入失败: {holiday_data.get('date')} - {str(e)}"))
                    continue
            
            self.stdout.write(f"\n   📊 导入统计:")
            self.stdout.write(f"     - 成功: {imported_count} 条")
            self.stdout.write(f"     - 跳过: {skipped_count} 条")
            
            if imported_count > 0:
                self.stdout.write(self.style.SUCCESS(f"\n   ✅ {year} 年数据导入完成！"))
            else:
                self.stdout.write(self.style.WARNING(f"\n   ⚠️  {year} 年数据已是最新（没有新数据）"))
                
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"   ❌ JSON文件不存在: {json_file}"))
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"   ❌ JSON解析失败: {str(e)}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"   ❌ 导入失败: {str(e)}"))

