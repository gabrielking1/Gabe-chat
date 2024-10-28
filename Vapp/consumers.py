import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Messages
from django.contrib.auth.models import User

class OrderConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.order_id = self.scope['url_route']['kwargs']['order_id']
        self.room_group_name = f'order_{self.order_id}'

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

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message', None)
        sender = text_data_json.get('sender', None)
        receiver = text_data_json.get('receiver', None)
        typing = text_data_json.get('typing', False)

        if typing:
            # Fetch sender username
            sender_username = await self.get_username(sender)
            # Send typing notification only to the receiver
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_typing',
                    'sender_username': sender_username,
                    'receiver': receiver
                }
            )
        elif message and sender and receiver:
            # Save message to the database
            await self.save_message(message, sender, receiver)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender,
                    'receiver': receiver
                }
            )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        receiver = event['receiver']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': message,
            'sender': sender,
            'receiver': receiver
        }))

    async def chat_typing(self, event):
        sender_username = event['sender_username']
        receiver = event['receiver']

        # Send typing notification to WebSocket only if the receiver is the current user
        if self.scope['user'].id == int(receiver):
            await self.send(text_data=json.dumps({
                'type': 'typing',
                'sender_username': sender_username,
            }))

    @database_sync_to_async
    def save_message(self, message, sender, receiver):
        Messages.objects.create(
            order_id=self.order_id,
            sender_id=sender,
            receiver_id=receiver,
            message=message
        )

    @database_sync_to_async
    def get_username(self, user_id):
        try:
            user = User.objects.get(id=user_id)
            return user.username
        except User.DoesNotExist:
            return "Unknown User"
