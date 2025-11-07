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
    access_token = models.CharField(max_length=200, blank=True, verbose_name='访问令牌')
    refresh_token = models.CharField(max_length=200, blank=True, verbose_name='刷新令牌')
    photo_url = models.URLField(blank=True, verbose_name='头像URL')
    nickname = models.CharField(max_length=100, blank=True, verbose_name='QQ昵称')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'QQ用户'
        verbose_name_plural = 'QQ用户列表'
    
    def __str__(self):
        return f"{self.user.username} - {self.openid}"

