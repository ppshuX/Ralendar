"""
Django 管理命令：导入节假日数据

使用方法:
    # 导入当前年份和未来2年
    python manage.py import_holidays
    
    # 导入指定年份
    python manage.py import_holidays --year 2025
    
    # 导入多个年份
    python manage.py import_holidays --start-year 2024 --end-year 2027
    
    # 强制替换已存在的数据
    python manage.py import_holidays --replace
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from api.utils.holiday_sync import HolidaySyncService


class Command(BaseCommand):
    help = '从 Timor API 导入节假日数据到数据库'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--year',
            type=int,
            help='指定要导入的年份'
        )
        parser.add_argument(
            '--start-year',
            type=int,
            help='起始年份（与 --end-year 一起使用）'
        )
        parser.add_argument(
            '--end-year',
            type=int,
            help='结束年份（与 --start-year 一起使用）'
        )
        parser.add_argument(
            '--replace',
            action='store_true',
            help='替换已存在的数据（默认跳过已存在的记录）'
        )
    
    def handle(self, *args, **options):
        year = options.get('year')
        start_year = options.get('start_year')
        end_year = options.get('end_year')
        replace = options.get('replace', False)
        
        service = HolidaySyncService()
        
        # 情况1: 指定单个年份
        if year:
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(f"🎯 导入 {year} 年节假日数据")
            self.stdout.write(f"{'='*60}\n")
            
            success = service.sync_year_holidays(year, replace=replace)
            
            if success:
                self.stdout.write(self.style.SUCCESS(f'\n✅ {year} 年数据导入成功！'))
            else:
                self.stdout.write(self.style.ERROR(f'\n❌ {year} 年数据导入失败！'))
        
        # 情况2: 指定年份范围
        elif start_year and end_year:
            if start_year > end_year:
                self.stdout.write(self.style.ERROR('❌ 起始年份不能大于结束年份！'))
                return
            
            service.sync_multiple_years(start_year, end_year, replace=replace)
            self.stdout.write(self.style.SUCCESS(f'\n✅ 批量导入完成！'))
        
        # 情况3: 默认导入（去年、今年、未来2年）
        else:
            current_year = timezone.now().year
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(f"🎯 导入默认年份范围: {current_year - 1} - {current_year + 2}")
            self.stdout.write(f"{'='*60}\n")
            
            service.sync_multiple_years(current_year - 1, current_year + 2, replace=replace)
            self.stdout.write(self.style.SUCCESS(f'\n✅ 默认范围导入完成！'))
        
        self.stdout.write('\n')

