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
    
    这个端点主要用于满足 OAuth2 规范的 redirect_uri 要求
    实际的 code 通过 AcWingOS.api.oauth2.authorize 的 callback 参数接收
    """
    # 返回一个简单的 HTML 页面，表示授权成功
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>授权成功</title>
        <style>
            body {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .container {
                text-align: center;
                padding: 40px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                backdrop-filter: blur(10px);
            }
            .success-icon {
                font-size: 64px;
                margin-bottom: 20px;
            }
            h1 {
                margin: 0 0 10px 0;
                font-size: 32px;
            }
            p {
                margin: 0;
                opacity: 0.9;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="success-icon">✅</div>
            <h1>授权成功</h1>
            <p>正在跳转回应用...</p>
        </div>
        <script>
            // 3秒后自动关闭窗口
            setTimeout(() => {
                window.close();
            }, 3000);
        </script>
    </body>
    </html>
    """
    return HttpResponse(html)

