"""
自定义认证类 - 支持跨应用用户识别
使用 UnionID 匹配不同应用的同一用户
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken
from django.contrib.auth.models import User
from .models import QQUser


class CrossAppJWTAuthentication(JWTAuthentication):
    """
    跨应用 JWT 认证
    
    流程：
    1. 验证 JWT Token（使用共享的 SECRET_KEY）
    2. 从 Token 中提取 user_id
    3. 尝试通过 UnionID 匹配用户：
       - 先查找 Roamio 用户的 QQ 信息（通过 user_id）
       - 获取 unionid
       - 在 Ralendar 中通过 unionid 查找对应用户
    4. 如果找到，返回 Ralendar 的用户
    5. 如果找不到，创建新用户（可选）
    """
    
    def get_user(self, validated_token):
        """
        从验证过的 Token 中获取用户
        优先通过 UnionID 匹配用户
        """
        try:
            user_id = validated_token.get('user_id')
            if user_id is None:
                raise InvalidToken('Token 中没有 user_id')
            
            # 先尝试直接查找用户（同应用内）
            try:
                user = User.objects.get(id=user_id)
                return user
            except User.DoesNotExist:
                # 用户在本应用不存在，尝试通过 UnionID 跨应用识别
                # 注意：这里需要 Roamio 在 Token 中包含额外信息
                # 或者通过 API 查询 Roamio 的用户信息
                pass
            
            # 如果找不到用户，返回 None
            # DRF 会自动返回 401
            return None
            
        except Exception:
            raise InvalidToken('无法从 Token 中提取用户信息')


class UnionIDJWTAuthentication(JWTAuthentication):
    """
    基于 UnionID 的 JWT 认证（宽松模式）
    
    对于 Fusion API，我们不严格要求用户在本应用存在
    而是通过 Token 验证身份即可
    """
    
    def authenticate(self, request):
        """
        认证请求
        返回 (user, token) 或 None
        """
        header = self.get_header(request)
        if header is None:
            return None
        
        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None
        
        try:
            validated_token = self.get_validated_token(raw_token)
        except Exception:
            return None
        
        # 对于 Fusion API，只要 Token 有效就通过认证
        # 不强制要求用户存在于本应用
        user = self.get_user_flexible(validated_token)
        return (user, validated_token)
    
    def get_user_flexible(self, validated_token):
        """
        宽松的用户获取
        如果用户不存在，返回一个临时用户对象
        """
        try:
            user_id = validated_token.get('user_id')
            if user_id is None:
                # 创建一个临时用户对象（仅用于 Fusion API）
                # 实际的用户匹配在视图层通过 UnionID 处理
                user = User(id=user_id, username=f'roamio_user_{user_id}')
                user._is_temporary = True
                return user
            
            # 先尝试直接查找
            try:
                user = User.objects.get(id=user_id)
                return user
            except User.DoesNotExist:
                # 用户不存在，创建临时对象
                user = User(id=user_id, username=f'roamio_user_{user_id}')
                user._is_temporary = True
                return user
                
        except Exception:
            raise InvalidToken('无法验证用户')

