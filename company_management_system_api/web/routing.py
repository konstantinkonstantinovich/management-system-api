from django.urls import path
from .consumers import VehiclesConsumer

ws_urlpatterns = {
    path('ws/vehicles', VehiclesConsumer.as_asgi())
}
