from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('events', views.EventViewSet, basename='event')
router.register('calendars', views.PublicCalendarViewSet, basename='calendar')

urlpatterns = [
    path('', include(router.urls)),
    path('lunar/', views.get_lunar_date, name='lunar'),
]

