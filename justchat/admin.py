from django.contrib import admin

from justchat.models import ChatHistory
from .models import Room


admin.site.register(
    Room,
    list_display=["id", "title", "staff_only"],
    list_display_links=["id", "title"],
)


admin.site.register(
    ChatHistory,
    list_display=["id", "a_party_user", "b_party_user", "message", "created_at"],
)
