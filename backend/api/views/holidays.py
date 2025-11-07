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


# 节假日数据文件路径
HOLIDAYS_DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')


def load_holidays_data(year):
    """加载节假日数据"""
    cache_key = f'holidays_{year}'
    holidays = cache.get(cache_key)
    
    if holidays is None:
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
    """检查指定日期是否是节假日"""
    date_str = request.GET.get('date')
    
    if not date_str:
        # 如果没有提供日期，使用今天
        target_date = date.today()
    else:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'error': '日期格式错误，请使用 YYYY-MM-DD 格式'}, status=400)
    
    holiday_info = get_holiday_info(target_date)
    
    if holiday_info:
        return Response({
            'date': target_date.strftime('%Y-%m-%d'),
            **holiday_info
        })
    else:
        return Response({
            'date': target_date.strftime('%Y-%m-%d'),
            'is_holiday': False,
            'is_workday': True,
            'holiday_name': None,
            'holiday_type': None
        })


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
    
    # 添加一些国际节日（可以根据日期判断）
    month_day = today.strftime('%m-%d')
    international_festivals = {
        '01-01': '元旦',
        '02-14': '情人节',
        '03-08': '国际妇女节',
        '04-01': '愚人节',
        '05-01': '国际劳动节',
        '05-04': '青年节',
        '06-01': '国际儿童节',
        '09-10': '教师节',
        '10-01': '国庆节',
        '12-25': '圣诞节'
    }
    
    if month_day in international_festivals:
        result['international_festivals'].append({
            'name': international_festivals[month_day],
            'type': 'international'
        })
    
    return Response(result)

