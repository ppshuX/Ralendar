"""
OpenWeatherMap天气API视图

提供天气查询功能
"""

import logging
import requests
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


# 天气状况中英文映射
WEATHER_TRANSLATION = {
    'clear sky': '晴',
    'few clouds': '少云',
    'scattered clouds': '多云',
    'broken clouds': '阴',
    'overcast clouds': '阴天',
    'shower rain': '阵雨',
    'rain': '雨',
    'light rain': '小雨',
    'moderate rain': '中雨',
    'heavy rain': '大雨',
    'thunderstorm': '雷暴',
    'snow': '雪',
    'mist': '雾',
    'haze': '霾',
    'fog': '雾',
}


@api_view(['GET'])
@permission_classes([AllowAny])
def get_weather(request):
    """
    获取指定城市的实时天气
    
    参数：
    - location: 城市名称（必填）
              例如：北京、上海、Beijing
    
    返回：
    - success: true/false
    - data: 天气数据
      - location: 城市名称
      - temperature: 温度（℃）
      - weather: 天气状况（如：晴、多云、阴）
      - windDir: 风向（暂不支持）
      - windScale: 风力等级（暂不支持）
      - humidity: 相对湿度（%）
      - feelsLike: 体感温度（℃）
      - updateTime: 更新时间
    """
    
    # 获取请求参数
    location = request.GET.get('location', '').strip()
    
    if not location:
        return Response({
            'success': False,
            'error': '请提供城市名称'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 检查API Key
    api_key = getattr(settings, 'OPENWEATHER_API_KEY', '') or getattr(settings, 'QWEATHER_API_KEY', '')
    if not api_key:
        logger.error('OpenWeatherMap API Key未配置')
        return Response({
            'success': False,
            'error': '天气服务未配置'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    try:
        # 调用OpenWeatherMap API - 实时天气
        url = 'https://api.openweathermap.org/data/2.5/weather'
        params = {
            'q': location,  # 城市名称
            'appid': api_key,  # API Key
            'units': 'metric',  # 使用摄氏度
            'lang': 'zh_cn'  # 中文描述
        }
        
        logger.info(f'请求OpenWeatherMap API: location={location}')
        response = requests.get(url, params=params, timeout=10)
        
        # 检查HTTP状态码
        if response.status_code == 401:
            logger.error('OpenWeatherMap API Key无效')
            return Response({
                'success': False,
                'error': 'API Key无效'
            }, status=status.HTTP_401_UNAUTHORIZED)
        elif response.status_code == 404:
            logger.error(f'城市未找到: {location}')
            return Response({
                'success': False,
                'error': f'未找到城市: {location}'
            }, status=status.HTTP_404_NOT_FOUND)
        
        response.raise_for_status()
        data = response.json()
        
        logger.info(f'OpenWeatherMap API响应成功: {location}')
        
        # 提取天气数据
        main = data.get('main', {})
        weather = data.get('weather', [{}])[0]
        
        # 翻译天气描述
        weather_desc = weather.get('description', '').lower()
        weather_cn = WEATHER_TRANSLATION.get(weather_desc, weather.get('description', '未知'))
        
        weather_data = {
            'location': data.get('name', location),  # 城市名称
            'temperature': str(int(main.get('temp', 0))),  # 温度（取整）
            'weather': weather_cn,  # 天气状况（中文）
            'windDir': '--',  # OpenWeatherMap不直接提供风向文字
            'windScale': '--',  # OpenWeatherMap不提供风力等级
            'humidity': str(main.get('humidity', '--')),  # 相对湿度
            'feelsLike': str(int(main.get('feels_like', 0))),  # 体感温度
            'updateTime': ''  # OpenWeatherMap不提供更新时间
        }
        
        logger.info(f'天气数据: {location} {weather_data["temperature"]}℃ {weather_data["weather"]}')
        
        return Response({
            'success': True,
            'data': weather_data
        })
        
    except requests.exceptions.Timeout:
        logger.error('OpenWeatherMap API请求超时')
        return Response({
            'success': False,
            'error': '天气服务请求超时，请稍后重试'
        }, status=status.HTTP_504_GATEWAY_TIMEOUT)
        
    except requests.exceptions.RequestException as e:
        logger.error(f'OpenWeatherMap API请求失败: {str(e)}')
        return Response({
            'success': False,
            'error': '无法连接到天气服务'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
    except Exception as e:
        logger.error(f'获取天气数据异常: {str(e)}', exc_info=True)
        return Response({
            'success': False,
            'error': '获取天气数据失败'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_location(request):
    """
    搜索城市（OpenWeatherMap不需要此功能，保留接口兼容性）
    
    参数：
    - location: 城市名称（必填）
    
    返回：
    - success: true/false
    - data: 直接返回输入的城市名
    """
    
    location = request.GET.get('location', '').strip()
    
    if not location:
        return Response({
            'success': False,
            'error': '请提供城市名称'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # OpenWeatherMap直接支持城市名查询，无需LocationID
    return Response({
        'success': True,
        'data': [{'name': location}]
    })

