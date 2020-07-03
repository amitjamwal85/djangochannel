from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
# import justchat.routing
from django.urls import path, re_path

from justchat.consumers import OMConsumer, ChatConsumer, UserChatConsumer

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter([
            # justchat.routing.websocket_urlpatterns,
            re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer),
            path("om/chat/", OMConsumer),
            path("user_chat/", UserChatConsumer),
        ])
    ),
})