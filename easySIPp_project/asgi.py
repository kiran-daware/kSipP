import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
import easySIPp.routing  # Replace `yourapp` with your actual app name

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'easySIPp_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": URLRouter(
        easySIPp.routing.websocket_urlpatterns
    ),
})
