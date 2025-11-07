"""
日历相关模型
"""
from django.db import models
from django.contrib.auth.models import User
from .event import Event


class PublicCalendar(models.Model):
    """公开日历（用于订阅）"""
    name = models.CharField(max_length=100, verbose_name='日历名称')
    url_slug = models.SlugField(unique=True, verbose_name='URL标识')
    description = models.TextField(blank=True, verbose_name='描述')
    is_public = models.BooleanField(default=True, verbose_name='是否公开')
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name='创建者'
    )
    events = models.ManyToManyField(
        Event, 
        blank=True, 
        related_name='calendars',
        verbose_name='日程列表'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '公开日历'
        verbose_name_plural = '公开日历列表'
    
    def __str__(self):
        return self.name

