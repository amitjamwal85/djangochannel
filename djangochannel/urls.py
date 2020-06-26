from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from rest_framework.documentation import include_docs_urls
from rest_framework.permissions import AllowAny
from api.views import UserAPIView
from djangochannel import settings
from justchat import views as chat_view
from rest_framework import routers
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', LoginView.as_view(), name="login"),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),
    path('docs/', include_docs_urls(title='Django DRF', permission_classes=[AllowAny])),

    # path('', chat_view.omchat, name='chat'),
    path('userchat', chat_view.userchat, name='user_chat'),
    path('chat_history', chat_view.chat_history, name='chat_history'),
    path('send_chat', chat_view.send_chat, name='send_chat')
]

router = routers.SimpleRouter()
router.register(r'users', UserAPIView)
urlpatterns += router.urls

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
