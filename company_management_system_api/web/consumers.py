import json
import os

from channels.generic.websocket import AsyncWebsocketConsumer
from api.models import Vehicle
from api.serializers import VehicleSerializer


os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"


class VehiclesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add('vehicles', self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard('vehicles', self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        vehicles = Vehicle.objects.filter(office_id=int(text_data))
        serializer = VehicleSerializer(vehicles, many=True)
        await self.send(text_data=json.dumps(serializer.data))

    async def send_vehicle(self, event):
        text_message = event['text']

        await self.send(text_data=json.dumps({'report_vehicle': text_message}))
