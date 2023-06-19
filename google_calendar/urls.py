from django.urls import path
from google_calendar.views import display_events

urlpatterns = [
    path('events/', display_events, name='display_events'),
]
