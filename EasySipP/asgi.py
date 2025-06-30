import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import kSipP.routing  # Replace `yourapp` with your actual app name

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'EasySipP.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        kSipP.routing.websocket_urlpatterns
    ),
})
