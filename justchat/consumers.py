import json
# from asgiref.sync import async_to_sync
# from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer, AsyncJsonWebsocketConsumer

from djangochannel import settings
from djangochannel.exceptions import ClientError
from justchat.utils import get_room_or_error, get_authenication


class UserChatConsumer(AsyncJsonWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.room_group_name = 'room'

    async def connect(self):
        print(f'Username: {self.scope["user"]}')
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            await self.accept()

    async def receive_json(self, content=None, byte_data=None):
        print(f"receive_json content: {content}")
        command = content.get("command", None)
        try:
            if command == "join":
                await self.join_room(content["user_id"])
            elif command == "send":
                await self.send_room(content["message"])
        except ClientError as e:
            print({"error": e.code})
            await self.send_json({"error": e.code})

    async def join_room(self, user_id):
        print(f"user_id: {user_id} {self.room_group_name}")
        check_status = await get_authenication(self.scope["user"])
        if check_status:
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name,
            )
            print("User added successfully")

    async def send_room(self, message):
        print(f"send_room: {message}")
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "username": self.scope["user"].username,
                "message": message,
            }
        )

    async def chat_message(self, event):
        print(f"chat_message: {event}")
        await self.send_json(
            {
                "msg_type": settings.MSG_TYPE_MESSAGE,
                "room": self.room_group_name,
                "username": event["username"],
                "message": event["message"],
            },
        )


####################################################################################################


class OMConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        print(f'Username: {self.scope["user"]}')
        if self.scope["user"].is_anonymous:
            await self.close()
        else:
            await self.accept()
        self.rooms = set()

    async def receive_json(self, content=None, byte_data=None):
        print(f"receive_json content: {content}")
        command = content.get("command", None)
        try:
            if command == "join":
                await self.join_room(content["room"])
            elif command == "leave":
                await self.leave_room(content["room"])
            elif command == "send":
                await self.send_room(content["room"], content["message"])
        except ClientError as e:
            await self.send_json({"error": e.code})

    async def join_room(self, room_id):
        print(f"join_room: {room_id}")
        room = await get_room_or_error(room_id, self.scope["user"])
        if settings.NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
            await self.channel_layer.group_send(
                room.group_name,
                {
                    "type": "chat.join",
                    "room_id": room_id,
                    "username": self.scope["user"].username,
                }
            )
            self.rooms.add(room_id)
            print(f"self.rooms:{self.rooms} :: self.channel_name:{self.channel_name}")
            # Add them to the group so they get room messages
            await self.channel_layer.group_add(
                room.group_name,
                self.channel_name,
            )
            # Instruct their client to finish opening the room
            await self.send_json({
                "join": str(room.id),
                "title": room.title,
            })

    async def leave_room(self, room_id):
        print(f"leave_room: {room_id}")
        room = await get_room_or_error(room_id, self.scope["user"])
        if settings.NOTIFY_USERS_ON_ENTER_OR_LEAVE_ROOMS:
            await self.channel_layer.group_send(
                room.group_name,
                {
                    "type": "chat.leave",
                    "room_id": room_id,
                    "username": self.scope["user"].username,
                }
            )
        self.rooms.discard(room_id)
        # Remove them from the group so they no longer get room messages
        await self.channel_layer.group_discard(
            room.group_name,
            self.channel_name,
        )
        # Instruct their client to finish closing the room
        await self.send_json({
            "leave": str(room.id),
        })

    async def send_room(self, room_id, message):
        print(f"room_id: {room_id}  :: send_room: {message}")
        print(f"send_room self.rooms : {self.rooms}")
        if int(room_id) not in self.rooms:
            raise ClientError("ROOM_ACCESS_DENIED")
        room = await get_room_or_error(room_id, self.scope["user"])
        await self.channel_layer.group_send(
            room.group_name,
            {
                "type": "chat.message",
                "room_id": room_id,
                "username": self.scope["user"].username,
                "message": message,
            }
        )

    async def chat_join(self, event):
        print(f"chat_join: {event}")
        await self.send_json(
            {
                "msg_type": settings.MSG_TYPE_ENTER,
                "room": event["room_id"],
                "username": event["username"],
            },
        )

    async def chat_leave(self, event):
        print(f"chat_leave: {event}")
        await self.send_json(
            {
                "msg_type": settings.MSG_TYPE_LEAVE,
                "room": event["room_id"],
                "username": event["username"],
            },
        )

    async def chat_message(self, event):
        print(f"chat_message: {event}")
        await self.send_json(
            {
                "msg_type": settings.MSG_TYPE_MESSAGE,
                "room": event["room_id"],
                "username": event["username"],
                "message": event["message"],
            },
        )








##############################################################################################################


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message
        }))

##############################################################################################################

# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         self.room_name = self.scope['url_route']['kwargs']['room_name']
#         self.room_group_name = 'chat_%s' % self.room_name
#
#         # Join room group
#         async_to_sync(self.channel_layer.group_add)(
#             self.room_group_name,
#             self.channel_name
#         )
#         self.accept()
#
#     def disconnect(self, close_code):
#         # Leave room group
#         async_to_sync(self.channel_layer.group_discard)(
#             self.room_group_name,
#             self.channel_name
#         )
#
#     # Receive message from WebSocket
#     def receive(self, text_data=None, bytes_data=None):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#         print(f"Receive message from WebSocket : {message}")
#         # Send message to room group
#         async_to_sync(self.channel_layer.group_send)(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message
#             }
#         )
#
#     # Receive message from room group
#     def chat_message(self, event):
#         message = event['message']
#         print(f"Receive message from room group : {message}")
#         # Send message to WebSocket
#         self.send(text_data=json.dumps({
#             'message': message
#         }))





# class ChatConsumer(WebsocketConsumer):
#     def connect(self):
#         self.accept()
#
#     def disconnect(self, close_code):
#         pass
#
#     def receive(self, text_data=None, bytes_data=None):
#         text_data_json = json.loads(text_data)
#         message = text_data_json['message']
#
#         self.send(text_data=json.dumps({
#             'message': message
#         }))

