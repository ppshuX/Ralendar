from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from .models import Event, PublicCalendar, AcWingUser
from .serializers import (
    EventSerializer, PublicCalendarSerializer,
    UserRegisterSerializer, UserSerializer
)
from lunarcalendar import Converter, Solar
import requests
from urllib.parse import quote


class EventViewSet(viewsets.ModelViewSet):
    """日程 CRUD API"""
    serializer_class = EventSerializer
    permission_classes = [AllowAny]  # 允许所有人访问，未登录用户使用匿名账户
    
    def get_queryset(self):
        # 只返回当前用户的日程（如果已登录）
        if self.request.user.is_authenticated:
            return Event.objects.filter(user=self.request.user)
        # 开发环境：返回所有日程
        return Event.objects.all()
    
    def perform_create(self, serializer):
        # 如果用户已登录，关联当前用户
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            # 开发环境：使用默认用户或创建匿名用户
            from django.contrib.auth.models import User
            default_user, _ = User.objects.get_or_create(username='anonymous')
            serializer.save(user=default_user)


class PublicCalendarViewSet(viewsets.ReadOnlyModelViewSet):
    """公开日历 API（只读）"""
    queryset = PublicCalendar.objects.filter(is_public=True)
    serializer_class = PublicCalendarSerializer
    lookup_field = 'url_slug'
    
    @action(detail=True, methods=['get'])
    def feed(self, request, url_slug=None):
        """返回 iCalendar 格式的日历订阅"""
        calendar = self.get_object()
        ics_content = self.generate_ics(calendar)
        return Response(
            {'ics': ics_content, 'events_count': calendar.events.count()},
            content_type='application/json'
        )
    
    def generate_ics(self, calendar):
        """生成 iCalendar 格式"""
        events = calendar.events.all()
        ics_lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            f"PRODID:-//KotlinCalendar//{calendar.name}//CN",
            f"X-WR-CALNAME:{calendar.name}",
        ]
        
        for event in events:
            ics_lines.extend([
                "BEGIN:VEVENT",
                f"UID:event-{event.id}@kotlincalendar.com",
                f"DTSTART:{event.start_time.strftime('%Y%m%dT%H%M%S')}",
                f"DTEND:{event.end_time.strftime('%Y%m%dT%H%M%S')}",
                f"SUMMARY:{event.title}",
                f"DESCRIPTION:{event.description}",
                f"LOCATION:{event.location}",
                "END:VEVENT",
            ])
        
        ics_lines.append("END:VCALENDAR")
        return "\n".join(ics_lines)


# ==================== 用户认证 API ====================
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """用户注册"""
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': '注册成功',
            'user': UserSerializer(user).data
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request):
    """获取当前登录用户信息"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


# ==================== AcWing OAuth2 登录 ====================
@api_view(['POST'])
@permission_classes([AllowAny])
def acwing_login(request):
    """AcWing 一键登录"""
    code = request.data.get('code')
    
    if not code:
        return Response({'error': '缺少授权码'}, status=status.HTTP_400_BAD_REQUEST)
    
    # AcWing 应用信息（从配置文件读取）
    from django.conf import settings
    ACWING_APPID = getattr(settings, 'ACWING_APPID', '7626')
    ACWING_SECRET = getattr(settings, 'ACWING_SECRET', '')
    
    try:
        # 第二步：申请 access_token 和 openid
        token_url = f"https://www.acwing.com/third_party/api/oauth2/access_token/?appid={ACWING_APPID}&secret={ACWING_SECRET}&code={code}"
        token_response = requests.get(token_url, timeout=10)
        token_data = token_response.json()
        
        if 'errcode' in token_data:
            return Response({
                'error': f"获取token失败: {token_data.get('errmsg', 'unknown error')}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        access_token = token_data['access_token']
        openid = token_data['openid']
        refresh_token = token_data.get('refresh_token', '')
        
        # 第三步：获取用户信息
        userinfo_url = f"https://www.acwing.com/third_party/api/meta/identity/getinfo/?access_token={access_token}&openid={openid}"
        userinfo_response = requests.get(userinfo_url, timeout=10)
        userinfo_data = userinfo_response.json()
        
        if 'errcode' in userinfo_data:
            return Response({
                'error': f"获取用户信息失败: {userinfo_data.get('errmsg', 'unknown error')}"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        username = userinfo_data['username']
        photo_url = userinfo_data.get('photo', '')
        
        # 查找或创建用户
        acwing_user = AcWingUser.objects.filter(openid=openid).first()
        
        if acwing_user:
            # 已存在的用户，更新token
            acwing_user.access_token = access_token
            acwing_user.refresh_token = refresh_token
            acwing_user.photo_url = photo_url
            acwing_user.save()
            user = acwing_user.user
            # 更新用户名（如果AcWing上修改了）
            if user.username != username:
                user.username = username
                user.save()
        else:
            # 新用户，创建账号
            # 检查用户名是否已存在，如果存在则添加后缀
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1
            
            user = User.objects.create_user(
                username=username,
                password=None  # AcWing登录不需要密码
            )
            
            AcWingUser.objects.create(
                user=user,
                openid=openid,
                access_token=access_token,
                refresh_token=refresh_token,
                photo_url=photo_url
            )
        
        # 生成JWT token
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'photo': photo_url
            }
        }, status=status.HTTP_200_OK)
        
    except requests.RequestException as e:
        return Response({
            'error': f'请求AcWing API失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({
            'error': f'登录失败: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== 农历 API ====================
@api_view(['GET'])
def get_lunar_date(request):
    """农历 API"""
    date_str = request.GET.get('date')  # 格式：2025-11-05
    
    if not date_str:
        return Response({'error': '请提供 date 参数'}, status=400)
    
    try:
        # 解析日期
        year, month, day = map(int, date_str.split('-'))
        
        # 转换为农历
        solar = Solar(year, month, day)
        lunar = Converter.Solar2Lunar(solar)
        
        # 生肖对照表
        zodiac_list = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
        zodiac = zodiac_list[(lunar.year - 4) % 12]
        
        # 月份中文
        month_cn = ['正', '二', '三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二']
        lunar_month = f"{month_cn[lunar.month - 1]}月"
        
        # 日期中文
        day_cn = ['初一', '初二', '初三', '初四', '初五', '初六', '初七', '初八', '初九', '初十',
                  '十一', '十二', '十三', '十四', '十五', '十六', '十七', '十八', '十九', '二十',
                  '廿一', '廿二', '廿三', '廿四', '廿五', '廿六', '廿七', '廿八', '廿九', '三十']
        lunar_day = day_cn[lunar.day - 1]
        
        return Response({
            'lunar_date': f"农历{lunar.year}年{lunar_month}{lunar_day}",
            'year': lunar.year,
            'month': lunar_month,
            'day': lunar_day,
            'zodiac': zodiac,
            'solar_date': date_str
        })
    except ValueError as e:
        return Response({'error': f'日期格式错误: {str(e)}'}, status=400)
    except Exception as e:
        return Response({'error': f'转换失败: {str(e)}'}, status=500)
