from rest_framework import serializers
from .models import Event, PublicCalendar


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'description', 'date_time', 'reminder_minutes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PublicCalendarSerializer(serializers.ModelSerializer):
    events_count = serializers.IntegerField(source='events.count', read_only=True)
    
    class Meta:
        model = PublicCalendar
        fields = ['id', 'name', 'url_slug', 'description', 'is_public', 'events_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class EventListSerializer(serializers.ModelSerializer):
    """精简版事件序列化器（用于列表展示）"""
    class Meta:
        model = Event
        fields = ['id', 'title', 'date_time']

