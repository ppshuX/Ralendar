"""
Holidays API - 节假日信息
"""
import json
import os
from datetime import datetime, date
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


# 节假日数据文件路径（从views/external/向上两级到api/，再进入data/）
HOLIDAYS_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')


def load_holidays_data(year):
    """加载节假日数据（优先从数据库，回退到JSON文件）"""
    cache_key = f'holidays_{year}'
    holidays = cache.get(cache_key)
    
    if holidays is None:
        # 优先从数据库加载
        from api.models import Holiday
        from datetime import date
        
        db_holidays = Holiday.objects.filter(date__year=year)
        
        if db_holidays.exists():
            # 从数据库构建JSON格式的数据结构
            holidays = {str(year): {}}
            
            for holiday in db_holidays.order_by('date'):
                date_str = holiday.date.strftime('%Y-%m-%d')
                
                if holiday.type == 'major':
                    # 主要节日：单个日期
                    holidays[str(year)][holiday.name] = date_str
                elif holiday.type == 'vacation' and holiday.holiday_group:
                    # 假期：添加到假期组
                    group_name = holiday.holiday_group
                    if group_name not in holidays[str(year)]:
                        holidays[str(year)][group_name] = []
                    if date_str not in holidays[str(year)][group_name]:
                        holidays[str(year)][group_name].append(date_str)
            
            # 对假期日期列表排序
            for key, value in holidays[str(year)].items():
                if isinstance(value, list):
                    holidays[str(year)][key] = sorted(value)
            
            # 缓存 24 小时
            cache.set(cache_key, holidays, 86400)
        else:
            # 回退到JSON文件
            file_path = os.path.join(HOLIDAYS_DATA_DIR, f'holidays_{year}.json')
            
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    holidays = json.load(f)
                # 缓存 24 小时
                cache.set(cache_key, holidays, 86400)
            else:
                holidays = {}
    
    return holidays


def get_holiday_info(target_date):
    """获取指定日期的节假日信息"""
    year = target_date.year
    holidays_data = load_holidays_data(year)
    
    if str(year) not in holidays_data:
        return None
    
    year_data = holidays_data[str(year)]
    date_str = target_date.strftime('%Y-%m-%d')
    
    # 检查是否是节假日
    holiday_info = {
        'is_holiday': False,
        'is_workday': False,
        'holiday_name': None,
        'holiday_type': None
    }
    
    # 检查主要节假日
    for holiday_name, holiday_date in year_data.items():
        if holiday_date == date_str:
            holiday_info['is_holiday'] = True
            holiday_info['holiday_name'] = holiday_name
            holiday_info['holiday_type'] = 'major'
            return holiday_info
    
    # 检查节假日假期
    for holiday_name, holiday_dates in year_data.items():
        if isinstance(holiday_dates, list) and date_str in holiday_dates:
            holiday_info['is_holiday'] = True
            # 提取节假日名称（去掉"假期"）
            holiday_info['holiday_name'] = holiday_name.replace('假期', '')
            holiday_info['holiday_type'] = 'vacation'
            return holiday_info
    
    return holiday_info


@api_view(['GET'])
@permission_classes([AllowAny])
def get_holidays(request):
    """获取指定年份的节假日列表"""
    year = request.GET.get('year', str(datetime.now().year))
    
    try:
        year = int(year)
        holidays_data = load_holidays_data(year)
        
        if str(year) not in holidays_data:
            return Response({
                'year': year,
                'holidays': [],
                'message': f'{year}年节假日数据未找到'
            })
        
        year_data = holidays_data[str(year)]
        holidays_list = []
        
        # 整理节假日数据
        for holiday_name, holiday_date in year_data.items():
            if isinstance(holiday_date, str):
                # 单个日期
                holidays_list.append({
                    'name': holiday_name,
                    'date': holiday_date,
                    'type': 'major'
                })
            elif isinstance(holiday_date, list):
                # 假期日期范围
                holidays_list.append({
                    'name': holiday_name,
                    'dates': holiday_date,
                    'start_date': holiday_date[0],
                    'end_date': holiday_date[-1],
                    'type': 'vacation',
                    'days': len(holiday_date)
                })
        
        return Response({
            'year': year,
            'holidays': holidays_list
        })
    except ValueError:
        return Response({'error': '年份格式错误'}, status=400)
    except Exception as e:
        return Response({'error': f'获取节假日失败: {str(e)}'}, status=500)


@api_view(['GET'])
@permission_classes([AllowAny])
def check_holiday(request):
    """检查指定日期的节假日（包括法定、国际、传统节日）"""
    date_str = request.GET.get('date')
    
    if not date_str:
        target_date = date.today()
    else:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': '日期格式错误，请使用 YYYY-MM-DD 格式'}, status=400)
    
    holiday_info = get_holiday_info(target_date)
    month_day = target_date.strftime('%m-%d')
    international_festivals_dict = {
        '01-01': {'name': '元旦', 'emoji': '🎊'},
        '02-14': {'name': '情人节', 'emoji': '💕'},
        '03-08': {'name': '国际妇女节', 'emoji': '👩'},
        '03-12': {'name': '植树节', 'emoji': '🌳'},
        '04-01': {'name': '愚人节', 'emoji': '🤡'},
        '05-01': {'name': '国际劳动节', 'emoji': '💪'},
        '05-04': {'name': '青年节', 'emoji': '🎓'},
        '06-01': {'name': '国际儿童节', 'emoji': '🧒'},
        '07-01': {'name': '建党节', 'emoji': '🎉'},
        '08-01': {'name': '建军节', 'emoji': '🎖️'},
        '09-10': {'name': '教师节', 'emoji': '📚'},
        '10-01': {'name': '国庆节', 'emoji': '🇨🇳'},
        '10-31': {'name': '万圣节', 'emoji': '🎃'},
        '11-11': {'name': '光棍节 / 双11购物节', 'emoji': '1️⃣'},
        '12-24': {'name': '平安夜', 'emoji': '🎄'},
        '12-25': {'name': '圣诞节', 'emoji': '🎅'}
    }
    
    festivals_list = []
    
    if holiday_info and holiday_info['is_holiday']:
        holiday_emoji = '🎉'
        for key, festival in international_festivals_dict.items():
            if festival['name'] in holiday_info['holiday_name']:
                holiday_emoji = festival['emoji']
                break
        
        festivals_list.append({
            'name': holiday_info['holiday_name'],
            'emoji': holiday_emoji,
            'type': 'legal'
        })
    
    if month_day in international_festivals_dict:
        festival = international_festivals_dict[month_day]
        if not any(f['name'] == festival['name'] for f in festivals_list):
            festivals_list.append({
                'name': festival['name'],
                'emoji': festival['emoji'],
                'type': 'international'
            })
    
    try:
        from lunarcalendar import Converter, Solar, Lunar
        
        traditional_festival_defs = [
            (1, 1, '春节', '🧨'),
            (1, 15, '元宵节', '🏮'),
            (5, 5, '端午节', '🐉'),
            (7, 7, '七夕节', '🎋'),
            (7, 15, '中元节', '🪔'),
            (8, 15, '中秋节', '🥮'),
            (9, 9, '重阳节', '🍵'),
            (12, 30, '除夕', '🏮'),
        ]
        
        for lunar_month, lunar_day, festival_name, emoji in traditional_festival_defs:
            try:
                lunar_date = Lunar(target_date.year, lunar_month, lunar_day, isLeapMonth=False)
                solar_date = Converter.Lunar2Solar(lunar_date)
                if solar_date.month == target_date.month and solar_date.day == target_date.day:
                    if not any(f['name'] == festival_name for f in festivals_list):
                        festivals_list.append({
                            'name': festival_name,
                            'emoji': emoji,
                            'type': 'traditional'
                        })
            except Exception:
                pass
        
        lunar_solar = Solar(target_date.year, target_date.month, target_date.day)
        lunar = Converter.Solar2Lunar(lunar_solar)
        
        month_cn = ['正', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二']
        lunar_month_str = f"{month_cn[lunar.month - 1]}月"
        
        day_cn = ['初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
                  '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                  '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十']
        lunar_day_str = day_cn[lunar.day - 1]
        
        lunar_str = f"{lunar_month_str}{lunar_day_str}"
    except Exception as e:
        logger.warning(f"获取农历失败: {e}")
        lunar_str = "加载中..."
    
    # 将 festivals_list 按类型分组，以匹配前端期望的数据结构
    traditional_festivals = [f for f in festivals_list if f.get('type') == 'traditional']
    international_festivals = [f for f in festivals_list if f.get('type') == 'international']
    legal_festivals = [f for f in festivals_list if f.get('type') == 'legal']
    
    # 确保 festivals 始终是列表（Android端需要）
    festivals_array = festivals_list if festivals_list else []
    
    # 构建完整的节日信息（前端期望的数据结构）
    result = {
        'date': target_date.strftime('%Y-%m-%d'),
        'is_holiday': holiday_info['is_holiday'] if holiday_info else False,
        'lunar': lunar_str,
        'festivals': festivals_array,  # 始终返回列表，即使是空列表
        # 为了兼容前端，也提供分组的数据
        'traditional_festivals': traditional_festivals if traditional_festivals else [],
        'international_festivals': international_festivals + legal_festivals if (international_festivals or legal_festivals) else []
    }
    
    return Response(result)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_today_holidays(request):
    """获取今日节假日和节日信息"""
    today = date.today()
    
    # 获取节假日信息
    holiday_info = get_holiday_info(today)
    
    # 获取传统节日（农历）
    # 这里可以扩展，添加更多传统节日
    
    result = {
        'date': today.strftime('%Y-%m-%d'),
        'holiday': holiday_info if holiday_info and holiday_info['is_holiday'] else None,
        'traditional_festivals': [],
        'international_festivals': []
    }
    
    # 添加一些国际节日和特殊日子（可以根据日期判断）
    month_day = today.strftime('%m-%d')
    international_festivals = {
        '01-01': {'name': '元旦', 'emoji': '🎊'},
        '02-14': {'name': '情人节', 'emoji': '💕'},
        '03-08': {'name': '国际妇女节', 'emoji': '👩'},
        '03-12': {'name': '植树节', 'emoji': '🌳'},
        '04-01': {'name': '愚人节', 'emoji': '🤡'},
        '05-01': {'name': '国际劳动节', 'emoji': '💪'},
        '05-04': {'name': '青年节', 'emoji': '🎓'},
        '06-01': {'name': '国际儿童节', 'emoji': '🧒'},
        '07-01': {'name': '建党节', 'emoji': '🎉'},
        '08-01': {'name': '建军节', 'emoji': '🎖️'},
        '09-10': {'name': '教师节', 'emoji': '📚'},
        '10-01': {'name': '国庆节', 'emoji': '🇨🇳'},
        '11-11': {'name': '光棍节 / 双11购物节', 'emoji': '1️⃣'},
        '12-24': {'name': '平安夜', 'emoji': '🎄'},
        '12-25': {'name': '圣诞节', 'emoji': '🎅'}
    }
    
    if month_day in international_festivals:
        festival = international_festivals[month_day]
        result['international_festivals'].append({
            'name': festival['name'],
            'emoji': festival['emoji'],
            'type': 'international'
        })
    
    try:
        from lunarcalendar import Converter, Solar, Lunar
        
        traditional_festival_defs = [
            (1, 1, '春节', '🧨'),
            (1, 15, '元宵节', '🏮'),
            (5, 5, '端午节', '🐉'),
            (7, 7, '七夕节', '🎋'),
            (7, 15, '中元节', '🪔'),
            (8, 15, '中秋节', '🥮'),
            (9, 9, '重阳节', '🍵'),
            (12, 30, '除夕', '🏮'),
        ]
        
        today_month_day = today.strftime('%m-%d')
        
        for lunar_month, lunar_day, festival_name, emoji in traditional_festival_defs:
            try:
                lunar_date = Lunar(today.year, lunar_month, lunar_day, isLeapMonth=False)
                solar_date = Converter.Lunar2Solar(lunar_date)
                solar_md = f"{solar_date.month:02d}-{solar_date.day:02d}"
                if solar_md == today_month_day:
                    result['traditional_festivals'].append({
                        'name': festival_name,
                        'emoji': emoji,
                        'type': 'traditional'
                    })
            except Exception:
                pass
    except Exception as e:
        logger.warning(f"获取农历节日失败: {e}")
    
    return Response(result)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_festival_detail(request):
    """
    获取节日详细信息（从本地JSON读取，不使用AI）
    
    GET /api/festivals/detail/?name=国庆节
    或
    GET /api/festivals/detail/?date=2025-10-01
    
    响应:
    {
        "name": "国庆节",
        "emoji": "🇨🇳",
        "type": "legal",
        "introduction": "...",
        "origin": "...",
        "customs": [...],
        "food": [...],
        "activities": [...]
    }
    """
    festival_name = request.GET.get('name')
    festival_date = request.GET.get('date')
    
    if not festival_name and not festival_date:
        return Response({'error': '请提供节日名称或日期'}, status=400)
    
    try:
        # 加载节日信息数据
        data_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'festivals_info.json')
        
        if not os.path.exists(data_file):
            logger.error(f"节日数据文件不存在: {data_file}")
            return Response({'error': '节日数据文件不存在'}, status=500)
        
        with open(data_file, 'r', encoding='utf-8') as f:
            festivals_data = json.load(f)
        
        # 如果提供了日期，先转换为MM-DD格式
        if festival_date:
            try:
                target_date = datetime.strptime(festival_date, '%Y-%m-%d')
                year = str(target_date.year)
                month_day = target_date.strftime('%m-%d')
                
                if year in festivals_data and month_day in festivals_data[year]:
                    festival_info = festivals_data[year][month_day]
                    return Response(festival_info)
            except ValueError:
                return Response({'error': '日期格式错误'}, status=400)
        
        # 如果提供了名称，遍历查找（支持精确匹配和部分匹配）
        if festival_name:
            # 先尝试精确匹配
            for year_data in festivals_data.values():
                for date_key, festival_info in year_data.items():
                    if festival_info.get('name') == festival_name:
                        return Response(festival_info)
            
            # 如果精确匹配失败，尝试部分匹配（支持"光棍节 / 双11购物节"这样的复合名称）
            # 将查询名称按"/"分割，尝试匹配每个部分
            name_parts = [part.strip() for part in festival_name.split('/')]
            for year_data in festivals_data.values():
                for date_key, festival_info in year_data.items():
                    stored_name = festival_info.get('name', '')
                    # 检查查询名称的任何部分是否在存储的名称中
                    for part in name_parts:
                        if part and part in stored_name:
                            return Response(festival_info)
                    # 也检查存储名称的任何部分是否在查询名称中
                    stored_parts = [p.strip() for p in stored_name.split('/')]
                    for stored_part in stored_parts:
                        if stored_part and stored_part in festival_name:
                            return Response(festival_info)
        
        return Response({
            'error': '未找到节日信息',
            'message': f'未找到关于 {festival_name or festival_date} 的详细信息'
        }, status=404)
        
    except Exception as e:
        logger.error(f"获取节日详情失败: {e}")
        return Response({'error': f'获取节日详情失败: {str(e)}'}, status=500)

