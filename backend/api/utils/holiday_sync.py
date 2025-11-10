"""
节假日数据同步工具
支持从多个数据源同步节假日数据
"""
import requests
import json
from datetime import datetime, date
from typing import Dict, List, Optional
from django.db import transaction
from django.utils import timezone
from api.models import Holiday, DataSyncLog


class HolidaySyncService:
    """节假日数据同步服务"""
    
    # Timor API（免费、稳定）
    TIMOR_API_BASE = "http://timor.tech/api/holiday"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Ralendar/1.0 (Holiday Sync Service)'
        })
    
    def fetch_year_holidays_from_timor(self, year: int) -> Optional[Dict]:
        """
        从 Timor API 获取指定年份的节假日数据
        
        API 文档: http://timor.tech/api/holiday
        返回格式:
        {
            "code": 0,
            "holiday": {
                "01-01": {"holiday": true, "name": "元旦", "wage": 3, ...},
                ...
            }
        }
        """
        try:
            url = f"{self.TIMOR_API_BASE}/year/{year}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') == 0:
                return data.get('holiday', {})
            else:
                print(f"❌ Timor API 返回错误: {data.get('message', '未知错误')}")
                return None
                
        except requests.RequestException as e:
            print(f"❌ 网络请求失败: {str(e)}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败: {str(e)}")
            return None
    
    def fetch_date_holiday_from_timor(self, target_date: date) -> Optional[Dict]:
        """
        从 Timor API 查询指定日期的节假日信息
        
        返回格式:
        {
            "code": 0,
            "type": {
                "type": 0,  # 0:工作日 1:周末 2:节假日 3:节假日调休
                "name": "春节",
                "week": 5
            }
        }
        """
        try:
            date_str = target_date.strftime('%Y-%m-%d')
            url = f"{self.TIMOR_API_BASE}/info/{date_str}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('code') == 0:
                return data.get('type', {})
            else:
                return None
                
        except Exception as e:
            print(f"❌ 查询日期失败: {str(e)}")
            return None
    
    def parse_timor_data_to_holidays(self, year: int, timor_data: Dict) -> List[Dict]:
        """
        将 Timor API 数据转换为 Holiday 模型数据
        
        参数:
            year: 年份
            timor_data: Timor API 返回的节假日字典
        
        返回:
            Holiday 模型数据列表
        """
        holidays = []
        
        for date_key, info in timor_data.items():
            # date_key 格式: "01-01"
            date_str = f"{year}-{date_key}"
            
            try:
                holiday_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                print(f"⚠️  跳过无效日期: {date_str}")
                continue
            
            # 判断节假日类型
            is_holiday = info.get('holiday', False)
            name = info.get('name', '')
            wage = info.get('wage', 1)  # 1:正常 2:双倍 3:三倍
            
            if not is_holiday:
                continue  # 只处理节假日
            
            # 确定节日类型
            if wage == 3:
                # 三倍工资的是主要节日（法定假日）
                holiday_type = 'major'
                is_legal_holiday = True
            else:
                # 其他假期
                holiday_type = 'vacation'
                is_legal_holiday = False
            
            # 确定节假日分组
            holiday_group = None
            if '春节' in name:
                holiday_group = '春节假期'
            elif '国庆' in name or '中秋' in name:
                holiday_group = '国庆中秋假期'
            elif '清明' in name:
                holiday_group = '清明节假期'
            elif '劳动节' in name or '五一' in name:
                holiday_group = '劳动节假期'
            elif '端午' in name:
                holiday_group = '端午节假期'
            elif '元旦' in name:
                holiday_group = '元旦假期'
            
            # Emoji 映射
            emoji_map = {
                '元旦': '🎊',
                '春节': '🧨',
                '清明': '🌿',
                '劳动节': '💪',
                '五一': '💪',
                '端午': '🐉',
                '中秋': '🥮',
                '国庆': '🇨🇳'
            }
            emoji = '🎉'
            for keyword, em in emoji_map.items():
                if keyword in name:
                    emoji = em
                    break
            
            holidays.append({
                'date': holiday_date,
                'name': name,
                'type': holiday_type,
                'is_legal_holiday': is_legal_holiday,
                'is_rest_day': True,
                'is_workday': False,
                'holiday_group': holiday_group,
                'emoji': emoji,
                'description': f"{year}年{name}",
                'data_version': '1.0',
            })
        
        return holidays
    
    @transaction.atomic
    def import_holidays_to_db(self, holidays: List[Dict], replace: bool = False) -> int:
        """
        将节假日数据导入数据库
        
        参数:
            holidays: 节假日数据列表
            replace: 是否替换已存在的数据（默认跳过）
        
        返回:
            成功导入的记录数
        """
        imported_count = 0
        skipped_count = 0
        
        for holiday_data in holidays:
            try:
                # 检查是否已存在
                existing = Holiday.objects.filter(
                    date=holiday_data['date'],
                    name=holiday_data['name'],
                    type=holiday_data['type']
                ).first()
                
                if existing:
                    if replace:
                        # 更新现有记录
                        for key, value in holiday_data.items():
                            setattr(existing, key, value)
                        existing.save()
                        imported_count += 1
                        print(f"  ✓ 更新: {holiday_data['date']} - {holiday_data['name']}")
                    else:
                        skipped_count += 1
                        print(f"  - 跳过: {holiday_data['date']} - {holiday_data['name']} (已存在)")
                else:
                    # 创建新记录
                    Holiday.objects.create(**holiday_data)
                    imported_count += 1
                    print(f"  ✓ 新增: {holiday_data['date']} - {holiday_data['name']}")
                    
            except Exception as e:
                print(f"  ❌ 导入失败: {holiday_data.get('date')} - {str(e)}")
                continue
        
        print(f"\n📊 导入统计:")
        print(f"  - 成功: {imported_count} 条")
        print(f"  - 跳过: {skipped_count} 条")
        
        return imported_count
    
    def sync_year_holidays(self, year: int, replace: bool = False) -> bool:
        """
        同步指定年份的节假日数据
        
        参数:
            year: 年份
            replace: 是否替换已存在的数据
        
        返回:
            是否同步成功
        """
        print(f"\n🔄 开始同步 {year} 年节假日数据...")
        
        # 1. 从 Timor API 获取数据
        timor_data = self.fetch_year_holidays_from_timor(year)
        if not timor_data:
            print(f"❌ 获取 {year} 年数据失败")
            from datetime import date
            self._log_sync_result(
                data_type='holiday',
                status='failed',
                message=f'获取 {year} 年数据失败',
                sync_date=date(year, 1, 1),
                sync_date_end=date(year, 12, 31)
            )
            return False
        
        print(f"✓ 成功获取 {len(timor_data)} 天的数据")
        
        # 2. 解析数据
        holidays = self.parse_timor_data_to_holidays(year, timor_data)
        print(f"✓ 解析出 {len(holidays)} 条节假日记录")
        
        if not holidays:
            print(f"⚠️  {year} 年没有节假日数据")
            return True
        
        # 3. 导入数据库
        imported_count = self.import_holidays_to_db(holidays, replace=replace)
        
        # 4. 记录同步日志
        from datetime import date
        if imported_count > 0:
            self._log_sync_result(
                data_type='holiday',
                status='success',
                message=f'成功同步 {year} 年 {imported_count} 条记录',
                sync_date=date(year, 1, 1),
                sync_date_end=date(year, 12, 31),
                records_count=imported_count
            )
            print(f"\n✅ {year} 年节假日数据同步完成！")
            return True
        else:
            self._log_sync_result(
                data_type='holiday',
                status='success',
                message=f'{year} 年数据已是最新',
                sync_date=date(year, 1, 1),
                sync_date_end=date(year, 12, 31),
                records_count=0
            )
            print(f"\n✓ {year} 年数据已是最新")
            return True
    
    def sync_multiple_years(self, start_year: int, end_year: int, replace: bool = False):
        """
        同步多个年份的节假日数据
        
        参数:
            start_year: 起始年份
            end_year: 结束年份（包含）
            replace: 是否替换已存在的数据
        """
        print(f"\n{'='*60}")
        print(f"🚀 开始批量同步节假日数据 ({start_year} - {end_year})")
        print(f"{'='*60}")
        
        success_count = 0
        fail_count = 0
        
        for year in range(start_year, end_year + 1):
            if self.sync_year_holidays(year, replace=replace):
                success_count += 1
            else:
                fail_count += 1
        
        print(f"\n{'='*60}")
        print(f"✅ 批量同步完成！")
        print(f"  - 成功: {success_count} 年")
        print(f"  - 失败: {fail_count} 年")
        print(f"{'='*60}\n")
    
    def _log_sync_result(self, data_type: str, status: str, message: str, 
                         sync_date=None, sync_date_end=None, records_count=0):
        """记录同步结果到数据库"""
        try:
            from datetime import date
            DataSyncLog.objects.create(
                data_type=data_type,
                status=status,
                sync_date=sync_date or date.today(),
                sync_date_end=sync_date_end,
                records_count=records_count,
                error_message=message if status == 'failed' else None,
                completed_at=timezone.now() if status in ['success', 'failed'] else None
            )
        except Exception as e:
            print(f"⚠️  记录同步日志失败: {str(e)}")


# 便捷函数
def sync_holidays(year: int = None, replace: bool = False):
    """
    同步节假日数据（便捷函数）
    
    参数:
        year: 年份，如果为 None 则同步当前年份和未来2年
        replace: 是否替换已存在的数据
    """
    service = HolidaySyncService()
    
    if year:
        return service.sync_year_holidays(year, replace=replace)
    else:
        # 默认同步：去年、今年、未来2年（共4年）
        current_year = datetime.now().year
        service.sync_multiple_years(current_year - 1, current_year + 2, replace=replace)


def check_holiday(target_date: date) -> Dict:
    """
    检查指定日期是否是节假日（便捷函数）
    
    参数:
        target_date: 要检查的日期
    
    返回:
        节假日信息字典
    """
    service = HolidaySyncService()
    return service.fetch_date_holiday_from_timor(target_date)

