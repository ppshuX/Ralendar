"""
OAuth2 Callback Handler - AcWing 授权回调接收
"""
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(['GET'])
@permission_classes([AllowAny])
def acwing_oauth_callback(request):
    """
    AcWing OAuth2 回调接收端点
    
    在 AcWing acapp 环境中，这个端点会被 AcWingOS 调用
    需要返回包含 code 和 state 的响应，供 JavaScript callback 使用
    """
    # 获取 URL 参数中的 code 和 state
    code = request.GET.get('code', '')
    state = request.GET.get('state', '')
    
    # 返回一个包含 JavaScript 的 HTML 页面
    # 这个页面会将 code 和 state 传递给父窗口（如果是弹窗）或返回给调用者
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>授权中...</title>
        <script>
            // 准备返回数据
            var authData = {{
                code: "{code}",
                state: "{state}"
            }};
            
            // 如果是在 iframe 或弹窗中，通知父窗口
            if (window.opener) {{
                window.opener.postMessage(authData, '*');
                window.close();
            }} else if (window.parent && window.parent !== window) {{
                window.parent.postMessage(authData, '*');
            }} else {{
                // 否则直接返回（AcWingOS 会读取这个响应）
                document.write(JSON.stringify(authData));
            }}
        </script>
    </head>
    <body>
        <p>授权成功，正在返回...</p>
    </body>
    </html>
    """
    return HttpResponse(html)

