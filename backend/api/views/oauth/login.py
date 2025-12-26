"""
OAuth 授权页面的登录处理
用于在OAuth授权流程中的登录
"""
from django.shortcuts import redirect
from django.contrib.auth import login as django_login
from django.http import HttpResponse, HttpResponseRedirect
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
    
    # 如果 next_url 是相对路径，尝试从 session 恢复完整 URL
    if next_url == '/oauth/authorize' or not next_url.startswith('http'):
        saved_full_url = request.session.get('oauth_authorize_full_url')
        if saved_full_url:
            # 如果是相对路径，构建完整 URL
            if saved_full_url.startswith('/'):
                next_url = f"{request.scheme}://{request.get_host()}{saved_full_url}"
            else:
                next_url = saved_full_url
            logger.info(f"[OAuth Login] Recovered full next_url from session: {next_url}")
        else:
            # 如果 session 中没有，尝试从参数构建
            saved_params = request.session.get('oauth_authorize_params', {})
            if saved_params:
                from urllib.parse import urlencode
                params = {
                    'client_id': saved_params.get('client_id'),
                    'redirect_uri': saved_params.get('redirect_uri'),
                    'response_type': saved_params.get('response_type', 'code'),
                }
                if saved_params.get('state'):
                    params['state'] = saved_params.get('state')
                if saved_params.get('scope'):
                    params['scope'] = saved_params.get('scope')
                next_url = f"{request.scheme}://{request.get_host()}/oauth/authorize?{urlencode(params)}"
                logger.info(f"[OAuth Login] Reconstructed next_url from session params: {next_url}")
    
    if provider == 'acwing':
        # AcWing登录：重定向到AcWing授权页面
        ACWING_APPID = getattr(settings, 'ACWING_APPID', '7626')
        REDIRECT_URI = f"{request.scheme}://{request.get_host()}/oauth/login/callback/acwing/"
        
        request.session['oauth_next_url'] = next_url
        
        auth_url = (
            f"https://www.acwing.com/third_party/api/oauth2/web/authorize/"
            f"?appid={ACWING_APPID}&redirect_uri={REDIRECT_URI}&scope=userinfo"
        )
        logger.info(f"[OAuth Login] Redirecting to AcWing auth: {auth_url}")
        return redirect(auth_url)
    
    elif provider == 'qq':
        QQ_APPID = getattr(settings, 'QQ_APPID', '')
        
        # 验证 QQ_APPID 是否配置
        if not QQ_APPID:
            logger.error(f"[OAuth Login] QQ_APPID is not configured")
            return HttpResponse('QQ登录未配置，请联系管理员', status=500)
        
        REDIRECT_URI = f"{request.scheme}://{request.get_host()}/qq/callback"
        
        request.session['oauth_next_url'] = next_url
        logger.info(f"[OAuth Login] Storing next_url in session: {next_url}")
        import base64
        import urllib.parse
        encoded_next_url = base64.urlsafe_b64encode(next_url.encode('utf-8')).decode('utf-8')
        state_param = f"qq_oauth_{encoded_next_url}"
        
        # 确保 URL 参数正确编码
        encoded_redirect_uri = urllib.parse.quote(REDIRECT_URI, safe='')
        encoded_state = urllib.parse.quote(state_param, safe='')
        
        # 构建 URL 参数（使用字典方式，更安全）
        auth_params = {
            'response_type': 'code',
            'client_id': QQ_APPID,
            'redirect_uri': REDIRECT_URI,  # 使用原始 URI，让 urllib.parse.urlencode 处理编码
            'state': state_param,
            'unionid': '1'
        }
        
        # 使用 urlencode 确保所有参数正确编码
        from urllib.parse import urlencode
        query_string = urlencode(auth_params, safe='')
        auth_url = f"https://graph.qq.com/oauth2.0/authorize?{query_string}"
        
        # 验证 URL 格式
        if not auth_url.startswith('https://graph.qq.com/oauth2.0/authorize'):
            logger.error(f"[OAuth Login] Invalid QQ auth URL format: {auth_url}")
            return HttpResponse('QQ登录URL生成失败', status=500)
        
        if 'client_id=' not in auth_url or not QQ_APPID:
            logger.error(f"[OAuth Login] Missing client_id in URL: {auth_url}")
            return HttpResponse('QQ登录配置错误：缺少 client_id', status=500)
        
        # 验证 URL 长度（QQ API 可能有长度限制）
        if len(auth_url) > 2000:
            logger.warning(f"[OAuth Login] QQ auth URL is very long ({len(auth_url)} chars), may cause issues")
        
        logger.info(f"[OAuth Login] Redirecting to QQ auth (length: {len(auth_url)}): {auth_url[:150]}...")
        logger.info(f"[OAuth Login] Full QQ auth URL: {auth_url}")
        
        # 使用 HttpResponseRedirect 确保重定向执行，并设置正确的状态码
        response = HttpResponseRedirect(auth_url)
        response['Location'] = auth_url  # 显式设置 Location header
        return response
    
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
    
    next_url = request.session.pop('oauth_next_url', '/oauth/authorize')
    
    ACWING_APPID = getattr(settings, 'ACWING_APPID', '7626')
    ACWING_SECRET = getattr(settings, 'ACWING_SECRET', '')
    
    try:
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
        
        acwing_user = AcWingUser.objects.filter(openid=openid).first()
        
        if acwing_user:
            user = acwing_user.user
        else:
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
        
        django_login(request, user)
        
        # 确保 session 被保存（重要：跨域重定向可能导致 session 丢失）
        request.session.save()
        logger.info(f"[OAuth Login] User {user.id} logged in via AcWing, session saved, redirecting to {next_url}")
        return redirect(next_url)
        
    except Exception as e:
        logger.error(f"[OAuth Login] AcWing login error: {str(e)}")
        return HttpResponse(f'登录失败: {str(e)}', status=500)


@require_http_methods(["GET"])
@permission_classes([AllowAny])
@csrf_exempt
def oauth_login_callback_qq(request):
    """
    QQ登录回调处理（统一处理OAuth登录和普通QQ登录）
    
    这个函数被 /qq/callback 路由调用，QQ开放平台只能配置一个回调地址
    通过检查 session 中的 oauth_next_url 来判断是OAuth流程还是普通登录流程
    """
    from django.conf import settings
    from django.contrib.auth import login as django_login
    from django.contrib.auth.models import User
    from ...models import QQUser
    
    code = request.GET.get('code')
    if not code:
        return HttpResponse('缺少授权码', status=400)
    
    # 获取 state 参数（优先判断，因为这是最可靠的标识）
    state = request.GET.get('state', '')
    
    # 判断是否是 OAuth 授权流程：
    # 1. state 参数明确包含 qq_oauth_ 前缀（最可靠）
    # 2. session 中有 oauth_next_url（从 OAuth 授权页面跳转过来的）
    # 注意：不能仅凭 referer 判断，因为普通登录也可能有 referer
    is_oauth_flow = False
    next_url = None
    
    if state and state.startswith('qq_oauth_'):
        # 明确是 OAuth 流程（从 state 参数判断）
        try:
            import base64
            encoded_next_url = state.replace('qq_oauth_', '')
            decoded_next_url = base64.urlsafe_b64decode(encoded_next_url.encode('utf-8')).decode('utf-8')
            next_url = decoded_next_url
            is_oauth_flow = True
            logger.info(f"[QQ Callback] OAuth flow detected from state parameter, next_url: {next_url}")
        except Exception as e:
            logger.error(f"[QQ Callback] Failed to decode next_url from state: {str(e)}")
            # 如果解码失败，尝试从 session 恢复
            next_url = request.session.pop('oauth_next_url', None)
            if next_url:
                is_oauth_flow = True
                logger.info(f"[QQ Callback] Recovered next_url from session after state decode failed")
    else:
        # 检查 session 中是否有 oauth_next_url（从 OAuth 授权页面跳转过来的）
        next_url = request.session.pop('oauth_next_url', None)
        if next_url:
            is_oauth_flow = True
            logger.info(f"[QQ Callback] OAuth flow detected from session, next_url: {next_url}")
        elif state == 'qq':
            # state=qq 且没有 session，认为是普通登录
            is_oauth_flow = False
            logger.info(f"[QQ Callback] Normal QQ login detected (state=qq, no session)")
        else:
            # 没有 state 或 state 为空，检查 referer（仅作为最后手段）
            referer = request.META.get('HTTP_REFERER', '')
            if referer and 'oauth/authorize' in referer:
                from urllib.parse import urlparse, parse_qs
                parsed = urlparse(referer)
                query_params = parse_qs(parsed.query)
                if query_params:
                    from urllib.parse import urlencode
                    query_string = urlencode(query_params, doseq=True)
                    next_url = f"{parsed.path}?{query_string}"
                else:
                    next_url = parsed.path
                is_oauth_flow = True
                logger.info(f"[QQ Callback] OAuth flow detected from referer (fallback): {next_url}")
    
    QQ_APPID = getattr(settings, 'QQ_APPID', '')
    QQ_APPKEY = getattr(settings, 'QQ_APPKEY', '')
    
    # 验证配置
    if not QQ_APPID or not QQ_APPKEY:
        logger.error(f"[QQ Callback] QQ_APPID or QQ_APPKEY is not configured")
        return HttpResponse('QQ登录未配置，请联系管理员', status=500)
    
    try:
        REDIRECT_URI = f"{request.scheme}://{request.get_host()}/qq/callback"
        import urllib.parse
        encoded_redirect_uri = urllib.parse.quote(REDIRECT_URI, safe='')
        encoded_code = urllib.parse.quote(code, safe='')
        
        token_url = (
            f"https://graph.qq.com/oauth2.0/token"
            f"?grant_type=authorization_code&client_id={QQ_APPID}"
            f"&client_secret={QQ_APPKEY}&code={encoded_code}"
            f"&redirect_uri={encoded_redirect_uri}"
        )
        token_response = requests.get(token_url, timeout=10)
        token_text = token_response.text
        
        # 解析 token 响应（可能是 URL 编码格式）
        if 'error' in token_text:
            logger.error(f"[OAuth Login] QQ token error: {token_text}")
            return HttpResponse('获取token失败', status=400)
        
        import re
        access_token_match = re.search(r'access_token=([^&]+)', token_text)
        if not access_token_match:
            return HttpResponse('获取token失败', status=400)
        
        access_token = access_token_match.group(1)
        
        openid_url = f"https://graph.qq.com/oauth2.0/me?access_token={access_token}&unionid=1"
        openid_response = requests.get(openid_url, timeout=10)
        openid_text = openid_response.text
        
        # 解析 JSONP 响应
        import json
        openid_data = json.loads(openid_text.strip().lstrip('callback(').rstrip(');'))
        openid = openid_data.get('openid')
        unionid = openid_data.get('unionid', '')
        
        # 确保参数正确编码
        import urllib.parse
        encoded_access_token = urllib.parse.quote(access_token, safe='')
        encoded_openid = urllib.parse.quote(openid, safe='')
        
        userinfo_url = (
            f"https://graph.qq.com/user/get_user_info"
            f"?access_token={encoded_access_token}&oauth_consumer_key={QQ_APPID}&openid={encoded_openid}"
        )
        logger.info(f"[QQ Callback] Requesting user info from: {userinfo_url.split('?')[0]}...")
        userinfo_response = requests.get(userinfo_url, timeout=10)
        userinfo_data = userinfo_response.json()
        
        if userinfo_data.get('ret') != 0:
            logger.error(f"[OAuth Login] QQ userinfo error: {userinfo_data}")
            return HttpResponse('获取用户信息失败', status=400)
        
        nickname = userinfo_data.get('nickname', 'QQ用户')
        photo_url = userinfo_data.get('figureurl_qq_2', '')
        
        # 查找或创建用户（优先使用 UnionID，与 /api/auth/qq/callback/ 保持一致）
        qq_user = None
        
        if unionid:
            # 如果有 UnionID，优先通过 UnionID 查找（跨应用识别，更可靠）
            qq_user = QQUser.objects.filter(unionid=unionid).first()
            
            if qq_user:
                # 找到已有用户，更新 openid 和 token（因为不同应用的 openid 可能不同）
                qq_user.openid = openid
                qq_user.photo_url = photo_url
                qq_user.nickname = nickname
                qq_user.save()
                user = qq_user.user
                logger.info(f"[QQ Callback] Found existing user by UnionID: {user.username} (unionid: {unionid})")
            else:
                # 通过 UnionID 没找到，尝试通过 openid 查找（可能是旧数据）
                qq_user = QQUser.objects.filter(openid=openid).first()
                
                if qq_user:
                    # 找到已有用户，补充 UnionID
                    qq_user.unionid = unionid
                    qq_user.photo_url = photo_url
                    qq_user.nickname = nickname
                    qq_user.save()
                    user = qq_user.user
                    logger.info(f"[QQ Callback] Found existing user by openid, updated with UnionID: {user.username}")
        else:
            # 没有 unionid，回退到 openid 查找（向后兼容）
            qq_user = QQUser.objects.filter(openid=openid).first()
            
            if qq_user:
                user = qq_user.user
                # 更新用户信息
                qq_user.photo_url = photo_url
                qq_user.nickname = nickname
                qq_user.save()
                logger.info(f"[QQ Callback] Found existing user by openid: {user.username}")
        
        if not qq_user:
            # 新用户，创建账号
            import re
            safe_nickname = re.sub(r'[^\w\u4e00-\u9fff]', '_', nickname)[:30]
            if not safe_nickname:
                safe_nickname = f"QQ用户_{openid[:8]}"
            
            base_username = safe_nickname
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
                if counter > 1000:
                    username = f"QQ用户_{openid[:8]}_{counter}"
                    break
            
            user = User.objects.create_user(username=username, password=None)
            QQUser.objects.create(
                user=user,
                openid=openid,
                unionid=unionid or None,
                nickname=nickname,
                photo_url=photo_url
            )
            logger.info(f"[QQ Callback] Created new user: {username} (unionid: {unionid or 'None'})")
        
        django_login(request, user)
        
        # 确保 session 被保存（重要：跨域重定向可能导致 session 丢失）
        request.session.save()
        logger.info(f"[QQ Callback] User {user.id} logged in via QQ, session saved, is_oauth_flow: {is_oauth_flow}, next_url: {next_url}")
        
        if is_oauth_flow:
            # OAuth 授权流程：需要返回授权页面
            if not next_url:
                # 如果 next_url 丢失，尝试从 session 恢复
                saved_full_url = request.session.get('oauth_authorize_full_url')
                if saved_full_url:
                    if saved_full_url.startswith('/'):
                        next_url = f"{request.scheme}://{request.get_host()}{saved_full_url}"
                    else:
                        next_url = saved_full_url
                    logger.info(f"[QQ Callback] Recovered full next_url from session: {next_url}")
                else:
                    # 尝试从 session 恢复授权参数
                    saved_params = request.session.get('oauth_authorize_params', {})
                    if saved_params:
                        from urllib.parse import urlencode
                        params = {
                            'client_id': saved_params.get('client_id'),
                            'redirect_uri': saved_params.get('redirect_uri'),
                            'response_type': saved_params.get('response_type', 'code'),
                        }
                        if saved_params.get('state'):
                            params['state'] = saved_params.get('state')
                        if saved_params.get('scope'):
                            params['scope'] = saved_params.get('scope')
                        next_url = f"{request.scheme}://{request.get_host()}/oauth/authorize?{urlencode(params)}"
                        logger.info(f"[QQ Callback] Recovered next_url from session params: {next_url}")
                    else:
                        next_url = f"{request.scheme}://{request.get_host()}/oauth/authorize"
                        logger.warning(f"[QQ Callback] Using default next_url (no session params found)")
            
            # 确保 next_url 是完整 URL
            if next_url.startswith('/'):
                next_url = f"{request.scheme}://{request.get_host()}{next_url}"
            
            logger.info(f"[QQ Callback] User {user.id} logged in via QQ (OAuth flow), redirecting to: {next_url}")
            return HttpResponseRedirect(next_url)
        else:
            # 普通登录流程：生成JWT token并返回自动处理页面
            # 注意：不应该跳转到 oauth/authorize，因为这不是 OAuth 授权流程
            
            # 生成JWT token（前端需要token来验证登录状态）
            from rest_framework_simplejwt.tokens import RefreshToken
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            # 直接在主HTML中嵌入token值（更安全，不会出现在浏览器历史记录中）
            home_url = f"{request.scheme}://{request.get_host()}/"
            
            # 使用json.dumps确保字符串正确转义
            import json
            access_token_js = json.dumps(access_token)
            refresh_token_js = json.dumps(refresh_token)
            home_url_js = json.dumps(home_url)
            
            logger.info(f"[QQ Callback] Normal login, returning auto-handle page with JWT token")
            
            # 返回一个HTML页面，页面中的JavaScript会自动处理token并跳转
            # 注意：token直接嵌入在HTML中，不会出现在URL中，更安全
            return HttpResponse(
                f'''
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>QQ登录成功 - 正在保存登录状态</title>
                </head>
                <body style="font-family: Arial, sans-serif; padding: 30px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; margin: 0;">
                    <div style="background: white; padding: 40px; border-radius: 16px; box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2); max-width: 500px;">
                        <h1 style="color: #28a745; font-size: 28px; margin-bottom: 20px;">✅ QQ登录成功！</h1>
                        <p style="font-size: 16px; color: #606266; margin-bottom: 20px;">正在保存登录状态，请稍候...</p>
                    </div>
                    <script>
                        // 自动处理token保存和跳转
                        (function() {{
                            try {{
                                // 从HTML中嵌入的token值获取（更安全，不会出现在URL中）
                                const accessToken = {access_token_js};
                                const refreshToken = {refresh_token_js};
                                
                                if (accessToken && refreshToken) {{
                                    // 保存token到localStorage
                                    localStorage.setItem('access_token', accessToken);
                                    localStorage.setItem('refresh_token', refreshToken);
                                    console.log('[QQ Login] Tokens saved to localStorage successfully');
                                    
                                    // 跳转到主页
                                    setTimeout(() => {{
                                        window.location.href = {home_url_js};
                                    }}, 500);
                                }} else {{
                                    // 如果没有token，直接跳转
                                    console.warn('[QQ Login] No token found');
                                    setTimeout(() => {{
                                        window.location.href = {home_url_js};
                                    }}, 1000);
                                }}
                            }} catch (error) {{
                                console.error('[QQ Login] Error saving tokens:', error);
                                // 出错也跳转到主页
                                setTimeout(() => {{
                                    window.location.href = {home_url_js};
                                }}, 1000);
                            }}
                        }})();
                    </script>
                </body>
                </html>
                ''',
                content_type='text/html; charset=utf-8'
            )
        
    except Exception as e:
        logger.error(f"[OAuth Login] QQ login error: {str(e)}")
        return HttpResponse(f'登录失败: {str(e)}', status=500)

