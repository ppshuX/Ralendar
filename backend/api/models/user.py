"""
用户相关模型
"""
from django.db import models
from django.contrib.auth.models import User


class AcWingUser(models.Model):
    """AcWing 用户信息"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='acwing_profile',
        verbose_name='关联用户'
    )
    openid = models.CharField(max_length=100, unique=True, verbose_name='AcWing OpenID')
    access_token = models.CharField(max_length=200, blank=True, verbose_name='访问令牌')
    refresh_token = models.CharField(max_length=200, blank=True, verbose_name='刷新令牌')
    photo_url = models.URLField(blank=True, verbose_name='头像URL')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'AcWing用户'
        verbose_name_plural = 'AcWing用户列表'
    
    def __str__(self):
        return f"{self.user.username} - {self.openid}"


class QQUser(models.Model):
    """QQ 用户信息"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='qq_profile',
        verbose_name='关联用户'
    )
    openid = models.CharField(max_length=100, unique=True, verbose_name='QQ OpenID')
    unionid = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        db_index=True,
        verbose_name='QQ UnionID',
        help_text='QQ 互联 UnionID，用于跨应用识别同一用户'
    )
    access_token = models.CharField(max_length=200, blank=True, verbose_name='访问令牌')
    refresh_token = models.CharField(max_length=200, blank=True, verbose_name='刷新令牌')
    photo_url = models.URLField(blank=True, verbose_name='头像URL')
    nickname = models.CharField(max_length=100, blank=True, verbose_name='QQ昵称')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'QQ用户'
        verbose_name_plural = 'QQ用户列表'
        indexes = [
            models.Index(fields=['unionid'], name='qquser_unionid_idx'),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.openid}"


class UserMapping(models.Model):
    """
    用户账号映射表
    用于实现 Roamio 和 Ralendar 用户的关联
    """
    ralendar_user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='roamio_mapping',
        verbose_name='Ralendar 用户'
    )
    roamio_user_id = models.IntegerField(
        unique=True,
        verbose_name='Roamio 用户ID',
        help_text='Roamio 项目中的用户ID'
    )
    roamio_username = models.CharField(
        max_length=150,
        verbose_name='Roamio 用户名'
    )
    
    # QQ UnionID（作为统一标识）
    qq_unionid = models.CharField(
        max_length=100,
        unique=True,
        blank=True,
        null=True,
        verbose_name='QQ UnionID',
        help_text='QQ 互联 UnionID，用于跨应用识别同一用户'
    )
    
    # 同步状态
    sync_enabled = models.BooleanField(
        default=True,
        verbose_name='启用同步',
        help_text='是否启用 Roamio 和 Ralendar 之间的数据同步'
    )
    last_sync_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='最后同步时间'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户映射'
        verbose_name_plural = '用户映射表'
        indexes = [
            models.Index(fields=['roamio_user_id'], name='user_mapping_roamio_idx'),
            models.Index(fields=['qq_unionid'], name='user_mapping_unionid_idx'),
        ]
    
    def __str__(self):
        return f"Ralendar({self.ralendar_user.id}) <-> Roamio({self.roamio_user_id})"
