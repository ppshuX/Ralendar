"""
工具类路由
包括：农历转换、节假日查询
"""
from django.urls import path
from ..views import (
    get_lunar_date,
    get_holidays,
    check_holiday,
    get_today_holidays,
)

urlpatterns = [
    # 农历转换
    path('lunar/', get_lunar_date, name='lunar'),
    
    # 节假日查询
    path('holidays/', get_holidays, name='get_holidays'),
    path('holidays/check/', check_holiday, name='check_holiday'),
    path('holidays/today/', get_today_holidays, name='get_today_holidays'),
]

