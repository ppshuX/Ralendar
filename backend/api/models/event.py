"""
事件相关模型
"""
from django.db import models
from django.contrib.auth.models import User
from urllib.parse import quote


class Event(models.Model):
    """日程事件（融合版）"""
    
    # === 基础字段 ===
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='events',
        verbose_name='用户'
    )
    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(blank=True, verbose_name='描述')
    start_time = models.DateTimeField(verbose_name='开始时间')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    location = models.CharField(max_length=200, blank=True, verbose_name='地点名称')
    reminder_minutes = models.IntegerField(default=15, verbose_name='提前提醒分钟数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    # === 来源追踪字段（用于 Roamio 融合）===
    source_app = models.CharField(
        max_length=50,
        choices=[
            ('ralendar', 'Ralendar'),
            ('roamio', 'Roamio'),
        ],
        default='ralendar',
        verbose_name='来源应用'
    )
    source_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='来源对象ID'
    )
    related_trip_slug = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='关联旅行计划Slug',
        help_text='关联的 Roamio 旅行计划唯一标识'
    )
    
    # === 地图信息字段 ===
    latitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name='纬度',
        help_text='地点的纬度坐标（-90 到 90）'
    )
    longitude = models.FloatField(
        null=True,
        blank=True,
        verbose_name='经度',
        help_text='地点的经度坐标（-180 到 180）'
    )
    map_provider = models.CharField(
        max_length=20,
        choices=[
            ('baidu', '百度地图'),
            ('amap', '高德地图'),
            ('tencent', '腾讯地图'),
        ],
        default='baidu',
        verbose_name='地图服务商'
    )
    
    # === 提醒配置字段 ===
    email_reminder = models.BooleanField(
        default=False,
        verbose_name='邮件提醒',
        help_text='是否发送邮件提醒'
    )
    notification_sent = models.BooleanField(
        default=False,
        verbose_name='提醒已发送',
        help_text='标记提醒是否已发送'
    )
    
    class Meta:
        ordering = ['start_time']
        verbose_name = '日程'
        verbose_name_plural = '日程列表'
        indexes = [
            models.Index(fields=['user', 'start_time'], name='event_user_start_idx'),
            models.Index(fields=['source_app', 'source_id'], name='event_source_idx'),
            models.Index(fields=['related_trip_slug'], name='event_trip_idx'),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def map_url(self):
        """
        生成地图链接（用于导航）
        
        Returns:
            str: 地图 URL，如果没有坐标则返回 None
        """
        if not (self.latitude and self.longitude):
            return None
        
        title_encoded = quote(self.title)
        
        if self.map_provider == 'baidu':
            # 百度地图导航链接
            return (
                f"https://api.map.baidu.com/marker"
                f"?location={self.latitude},{self.longitude}"
                f"&title={title_encoded}"
                f"&content={quote(self.location or '')}"
                f"&output=html"
                f"&src=Ralendar"
            )
        elif self.map_provider == 'amap':
            # 高德地图导航链接（注意：高德使用 经度,纬度 顺序）
            return (
                f"https://uri.amap.com/marker"
                f"?position={self.longitude},{self.latitude}"
                f"&name={title_encoded}"
                f"&src=Ralendar"
            )
        elif self.map_provider == 'tencent':
            # 腾讯地图导航链接
            return (
                f"https://apis.map.qq.com/uri/v1/marker"
                f"?marker=coord:{self.latitude},{self.longitude};title:{title_encoded}"
                f"&referer=Ralendar"
            )
        
        return None
    
    @property
    def has_location(self):
        """是否有地理位置"""
        return bool(self.latitude and self.longitude)
    
    @property
    def is_from_roamio(self):
        """是否来自 Roamio"""
        return self.source_app == 'roamio'

