# Generated migration for calendar data models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0009_oauth_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='Holiday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True, help_text='日期')),
                ('name', models.CharField(max_length=50, help_text="节日名称，如'春节'")),
                ('type', models.CharField(max_length=20, choices=[('major', '主要节日'), ('vacation', '假期'), ('traditional', '传统节日'), ('international', '国际节日')], help_text='节日类型')),
                ('is_legal_holiday', models.BooleanField(default=False, help_text='是否法定假日')),
                ('is_rest_day', models.BooleanField(default=False, help_text='是否休息日')),
                ('is_workday', models.BooleanField(default=False, help_text='是否调休工作日')),
                ('holiday_group', models.CharField(blank=True, help_text="假期组名，如'春节假期'", max_length=50, null=True)),
                ('lunar_date', models.CharField(blank=True, help_text="农历日期，如'正月初一'", max_length=20, null=True)),
                ('description', models.TextField(blank=True, help_text='节日介绍', null=True)),
                ('emoji', models.CharField(default='🎉', help_text='Emoji 图标', max_length=10)),
                ('data_version', models.CharField(default='1.0', help_text='数据版本', max_length=20)),
                ('last_updated', models.DateTimeField(auto_now=True, help_text='最后更新时间')),
            ],
            options={
                'verbose_name': '节假日',
                'verbose_name_plural': '节假日列表',
                'db_table': 'calendar_holidays',
                'ordering': ['date'],
            },
        ),
        migrations.AddIndex(
            model_name='holiday',
            index=models.Index(fields=['date'], name='holiday_date_idx'),
        ),
        migrations.AddIndex(
            model_name='holiday',
            index=models.Index(fields=['type'], name='holiday_type_idx'),
        ),
        migrations.AddIndex(
            model_name='holiday',
            index=models.Index(fields=['is_legal_holiday'], name='holiday_legal_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='holiday',
            unique_together={('date', 'name', 'type')},
        ),
        migrations.CreateModel(
            name='LunarCalendar',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True, help_text='公历日期', unique=True)),
                ('lunar_year', models.IntegerField(help_text='农历年份')),
                ('lunar_month', models.CharField(help_text="农历月份，如'正月'", max_length=10)),
                ('lunar_day', models.CharField(help_text="农历日期，如'初一'", max_length=10)),
                ('lunar_date_cn', models.CharField(help_text="农历日期中文，如'甲辰年正月初一'", max_length=50)),
                ('zodiac', models.CharField(help_text="生肖，如'龙'", max_length=2)),
                ('ganzhi_year', models.CharField(help_text="年干支，如'甲辰'", max_length=4)),
                ('ganzhi_month', models.CharField(help_text='月干支', max_length=4)),
                ('ganzhi_day', models.CharField(help_text='日干支', max_length=4)),
                ('solar_term', models.CharField(blank=True, help_text="节气，如'立春'", max_length=10, null=True)),
                ('yi', models.JSONField(default=list, help_text='宜（适合做的事）')),
                ('ji', models.JSONField(default=list, help_text='忌（不宜做的事）')),
                ('chong', models.CharField(blank=True, help_text="相冲生肖，如'冲鼠'", max_length=20, null=True)),
                ('sha', models.CharField(blank=True, help_text="煞方位，如'煞北'", max_length=20, null=True)),
                ('ji_shen', models.JSONField(default=list, help_text='吉神')),
                ('xiong_shen', models.JSONField(default=list, help_text='凶神')),
                ('wu_xing', models.CharField(blank=True, help_text="五行，如'金'", max_length=20, null=True)),
                ('auspicious_level', models.IntegerField(default=3, help_text='吉凶等级：1=大凶, 3=平, 5=大吉')),
                ('data_version', models.CharField(default='1.0', max_length=20)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': '黄历',
                'verbose_name_plural': '黄历列表',
                'db_table': 'calendar_lunar_calendars',
                'ordering': ['date'],
            },
        ),
        migrations.AddIndex(
            model_name='lunarcalendar',
            index=models.Index(fields=['date'], name='lunar_date_idx'),
        ),
        migrations.AddIndex(
            model_name='lunarcalendar',
            index=models.Index(fields=['lunar_year', 'lunar_month'], name='lunar_year_month_idx'),
        ),
        migrations.AddIndex(
            model_name='lunarcalendar',
            index=models.Index(fields=['auspicious_level'], name='lunar_auspicious_idx'),
        ),
        migrations.CreateModel(
            name='DailyFortune',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(db_index=True, help_text='日期')),
                ('fortune_type', models.CharField(max_length=20, choices=[('zodiac', '生肖运势'), ('constellation', '星座运势')], help_text='运势类型')),
                ('zodiac', models.CharField(blank=True, help_text="生肖，如'龙'", max_length=2, null=True)),
                ('constellation', models.CharField(blank=True, help_text="星座，如'天蝎座'", max_length=20, null=True)),
                ('overall_score', models.IntegerField(default=50, help_text='综合运势评分（0-100）')),
                ('summary', models.TextField(help_text='运势总结')),
                ('love_score', models.IntegerField(default=50, help_text='爱情运势（0-100）')),
                ('career_score', models.IntegerField(default=50, help_text='事业运势（0-100）')),
                ('wealth_score', models.IntegerField(default=50, help_text='财运（0-100）')),
                ('health_score', models.IntegerField(default=50, help_text='健康运势（0-100）')),
                ('lucky_color', models.CharField(blank=True, help_text='幸运颜色', max_length=20, null=True)),
                ('lucky_number', models.CharField(blank=True, help_text='幸运数字', max_length=20, null=True)),
                ('lucky_direction', models.CharField(blank=True, help_text='幸运方位', max_length=20, null=True)),
                ('advice', models.TextField(blank=True, help_text='今日建议', null=True)),
                ('data_source', models.CharField(default='auto', help_text='数据来源：auto/api/user_input', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': '运势',
                'verbose_name_plural': '运势列表',
                'db_table': 'calendar_fortunes',
                'ordering': ['-date'],
            },
        ),
        migrations.AddIndex(
            model_name='dailyfortune',
            index=models.Index(fields=['date', 'fortune_type'], name='fortune_date_type_idx'),
        ),
        migrations.AddIndex(
            model_name='dailyfortune',
            index=models.Index(fields=['zodiac'], name='fortune_zodiac_idx'),
        ),
        migrations.AddIndex(
            model_name='dailyfortune',
            index=models.Index(fields=['constellation'], name='fortune_constellation_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='dailyfortune',
            unique_together={('date', 'fortune_type', 'zodiac', 'constellation')},
        ),
        migrations.CreateModel(
            name='UserFortune',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('birth_date', models.DateField(help_text='出生日期')),
                ('zodiac', models.CharField(help_text='生肖', max_length=2)),
                ('constellation', models.CharField(help_text='星座', max_length=20)),
                ('subscribe_zodiac', models.BooleanField(default=True, help_text='订阅生肖运势')),
                ('subscribe_constellation', models.BooleanField(default=True, help_text='订阅星座运势')),
                ('notify_daily', models.BooleanField(default=False, help_text='每日推送运势')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='fortune_profile', to=settings.AUTH_USER_MODEL, help_text='用户')),
            ],
            options={
                'verbose_name': '用户运势配置',
                'verbose_name_plural': '用户运势配置列表',
                'db_table': 'calendar_user_fortunes',
            },
        ),
        migrations.CreateModel(
            name='DataSyncLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_type', models.CharField(max_length=20, choices=[('holiday', '节假日'), ('lunar', '黄历'), ('fortune', '运势')], help_text='数据类型')),
                ('sync_date', models.DateField(help_text='同步日期范围开始')),
                ('sync_date_end', models.DateField(blank=True, help_text='同步日期范围结束', null=True)),
                ('status', models.CharField(choices=[('pending', '待同步'), ('syncing', '同步中'), ('success', '成功'), ('failed', '失败')], default='pending', help_text='同步状态', max_length=20)),
                ('records_count', models.IntegerField(default=0, help_text='同步记录数')),
                ('error_message', models.TextField(blank=True, help_text='错误信息', null=True)),
                ('started_at', models.DateTimeField(blank=True, help_text='开始时间', null=True)),
                ('completed_at', models.DateTimeField(blank=True, help_text='完成时间', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': '数据同步日志',
                'verbose_name_plural': '数据同步日志列表',
                'db_table': 'calendar_data_sync_logs',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='datasynclog',
            index=models.Index(fields=['data_type', 'status'], name='sync_log_type_status_idx'),
        ),
        migrations.AddIndex(
            model_name='datasynclog',
            index=models.Index(fields=['sync_date'], name='sync_log_date_idx'),
        ),
    ]
