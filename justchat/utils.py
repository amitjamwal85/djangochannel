from channels.db import database_sync_to_async

from djangochannel.exceptions import ClientError
from .models import Room


# This decorator turns this function from a synchronous function into an async one
# we can call from our async consumers, that handles Django DBs correctly.
@database_sync_to_async
def get_room_or_error(room_id, user):
    if not user.is_authenticated:
        raise ClientError("USER_HAS_TO_LOGIN")

    try:
        room = Room.objects.get(pk=room_id)
    except Room.DoesNotExist:
        raise ClientError("ROOM_INVALID")

    if room.staff_only and not user.is_staff:
        raise ClientError("ROOM_ACCESS_DENIED")
    return room
