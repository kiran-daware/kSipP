from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/sipp_logs/$', consumers.SippLogConsumer.as_asgi()),
]
