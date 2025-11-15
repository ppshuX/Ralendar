"""
OAuth 授权页面的登录处理
用于在OAuth授权流程中的登录
"""
from django.shortcuts import redirect
from django.contrib.auth import login as django_login
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
import requests
import logging

from django.contrib.auth.models import User
from ...models import AcWingUser, QQUser

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
@permission_classes([AllowAny])
def oauth_web_login(request):
    """
    OAuth授权页面的登录处理
    用于在OAuth授权流程中，用户未登录时跳转到登录页面
    
    URL: /oauth/login?provider=acwing&next=/oauth/authorize?...
    或: /oauth/login?provider=qq&next=/oauth/authorize?...
    """
    from django.conf import settings
    
    provider = request.GET.get('provider', 'acwing')  # acwing 或 qq
    next_url = request.GET.get('next', '/oauth/authorize')
    
    if provider == 'acwing':
        # AcWing登录：重定向到AcWing授权页面
        ACWING_APPID = getattr(settings, 'ACWING_APPID', '7626')
        REDIRECT_URI = f"{request.scheme}://{request.get_host()}/oauth/login/callback/acwing/"
        
        # 将 next_url 存储在 session 中，以便登录成功后重定向
        request.session['oauth_next_url'] = next_url
        
        auth_url = (
            f"https://www.acwing.com/third_party/api/oauth2/web/authorize/"
            f"?appid={ACWING_APPID}&redirect_uri={REDIRECT_URI}&scope=userinfo"
        )
        logger.info(f"[OAuth Login] Redirecting to AcWing auth: {auth_url}")
        return redirect(auth_url)
    
    elif provider == 'qq':
        # QQ登录：重定向到QQ授权页面
        QQ_APPID = getattr(settings, 'QQ_APPID', '')
        # 注意：QQ互联要求回调地址不能有末尾斜杠，且必须在QQ开放平台配置白名单
        REDIRECT_URI = f"{request.scheme}://{request.get_host()}/oauth/login/callback/qq"
        
        # 将 next_url 存储在 session 中
        request.session['oauth_next_url'] = next_url
        
        auth_url = (
            f"https://graph.qq.com/oauth2.0/authorize"
            f"?response_type=code&client_id={QQ_APPID}&redirect_uri={REDIRECT_URI}"
            f"&state=qq&unionid=1"
        )
        logger.info(f"[OAuth Login] Redirecting to QQ auth: {auth_url}")
        return redirect(auth_url)
    
    else:
        return HttpResponse(f'不支持的登录方式: {provider}', status=400)


@require_http_methods(["GET"])
@permission_classes([AllowAny])
@csrf_exempt
def oauth_login_callback_acwing(request):
    """AcWing登录回调处理"""
    from django.conf import settings
    
    code = request.GET.get('code')
    if not code:
        return HttpResponse('缺少授权码', status=400)
    
    # 获取存储的 next_url
    next_url = request.session.pop('oauth_next_url', '/oauth/authorize')
    
    ACWING_APPID = getattr(settings, 'ACWING_APPID', '7626')
    ACWING_SECRET = getattr(settings, 'ACWING_SECRET', '')
    
    try:
        # 获取 access_token 和 openid
        token_url = (
            f"https://www.acwing.com/third_party/api/oauth2/access_token/"
            f"?appid={ACWING_APPID}&secret={ACWING_SECRET}&code={code}"
        )
        token_response = requests.get(token_url, timeout=10)
        token_data = token_response.json()
        
        if 'errcode' in token_data:
            logger.error(f"[OAuth Login] AcWing token error: {token_data}")
            return HttpResponse('获取token失败', status=400)
        
        access_token = token_data['access_token']
        openid = token_data['openid']
        
        # 获取用户信息
        userinfo_url = (
            f"https://www.acwing.com/third_party/api/meta/identity/getinfo/"
            f"?access_token={access_token}&openid={openid}"
        )
        userinfo_response = requests.get(userinfo_url, timeout=10)
        userinfo_data = userinfo_response.json()
        
        if 'errcode' in userinfo_data:
            logger.error(f"[OAuth Login] AcWing userinfo error: {userinfo_data}")
            return HttpResponse('获取用户信息失败', status=400)
        
        username = userinfo_data['username']
        photo_url = userinfo_data.get('photo', '')
        
        # 查找或创建用户
        acwing_user = AcWingUser.objects.filter(openid=openid).first()
        
        if acwing_user:
            user = acwing_user.user
        else:
            # 创建新用户
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            
            user = User.objects.create_user(username=username, password=None)
            AcWingUser.objects.create(
                user=user,
                openid=openid,
                access_token=access_token,
                photo_url=photo_url
            )
        
        # 使用Django的login函数设置session
        django_login(request, user)
        logger.info(f"[OAuth Login] User {user.id} logged in via AcWing, redirecting to {next_url}")
        
        # 重定向回OAuth授权页面
        return redirect(next_url)
        
    except Exception as e:
        logger.error(f"[OAuth Login] AcWing login error: {str(e)}")
        return HttpResponse(f'登录失败: {str(e)}', status=500)


@require_http_methods(["GET"])
@permission_classes([AllowAny])
@csrf_exempt
def oauth_login_callback_qq(request):
    """QQ登录回调处理"""
    from django.conf import settings
    
    code = request.GET.get('code')
    if not code:
        return HttpResponse('缺少授权码', status=400)
    
    # 获取存储的 next_url
    next_url = request.session.pop('oauth_next_url', '/oauth/authorize')
    
    QQ_APPID = getattr(settings, 'QQ_APPID', '')
    QQ_APPKEY = getattr(settings, 'QQ_APPKEY', '')
    
    try:
        # 获取 access_token
        # 注意：回调地址必须与授权时的地址完全一致（不能有末尾斜杠）
        REDIRECT_URI = f"{request.scheme}://{request.get_host()}/oauth/login/callback/qq"
        token_url = (
            f"https://graph.qq.com/oauth2.0/token"
            f"?grant_type=authorization_code&client_id={QQ_APPID}"
            f"&client_secret={QQ_APPKEY}&code={code}"
            f"&redirect_uri={REDIRECT_URI}"
        )
        token_response = requests.get(token_url, timeout=10)
        token_text = token_response.text
        
        # 解析 token 响应（可能是 URL 编码格式）
        if 'error' in token_text:
            logger.error(f"[OAuth Login] QQ token error: {token_text}")
            return HttpResponse('获取token失败', status=400)
        
        # 解析 access_token
        import re
        access_token_match = re.search(r'access_token=([^&]+)', token_text)
        if not access_token_match:
            return HttpResponse('获取token失败', status=400)
        
        access_token = access_token_match.group(1)
        
        # 获取 openid 和 unionid
        openid_url = f"https://graph.qq.com/oauth2.0/me?access_token={access_token}&unionid=1"
        openid_response = requests.get(openid_url, timeout=10)
        openid_text = openid_response.text
        
        # 解析 JSONP 响应
        import json
        openid_data = json.loads(openid_text.strip().lstrip('callback(').rstrip(');'))
        openid = openid_data.get('openid')
        unionid = openid_data.get('unionid', '')
        
        # 获取用户信息
        userinfo_url = (
            f"https://graph.qq.com/user/get_user_info"
            f"?access_token={access_token}&oauth_consumer_key={QQ_APPID}&openid={openid}"
        )
        userinfo_response = requests.get(userinfo_url, timeout=10)
        userinfo_data = userinfo_response.json()
        
        if userinfo_data.get('ret') != 0:
            logger.error(f"[OAuth Login] QQ userinfo error: {userinfo_data}")
            return HttpResponse('获取用户信息失败', status=400)
        
        nickname = userinfo_data.get('nickname', 'QQ用户')
        avatar = userinfo_data.get('figureurl_qq_2', '')
        
        # 查找或创建用户
        qq_user = QQUser.objects.filter(openid=openid).first()
        
        if qq_user:
            user = qq_user.user
        else:
            # 创建新用户
            base_username = nickname
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            
            user = User.objects.create_user(username=username, password=None)
            QQUser.objects.create(
                user=user,
                openid=openid,
                unionid=unionid,
                nickname=nickname,
                avatar=avatar
            )
        
        # 使用Django的login函数设置session
        django_login(request, user)
        logger.info(f"[OAuth Login] User {user.id} logged in via QQ, redirecting to {next_url}")
        
        # 重定向回OAuth授权页面
        return redirect(next_url)
        
    except Exception as e:
        logger.error(f"[OAuth Login] QQ login error: {str(e)}")
        return HttpResponse(f'登录失败: {str(e)}', status=500)

