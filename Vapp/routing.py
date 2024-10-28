from django.urls import re_path, path
from . import consumers

websocket_urlpatterns = [
    path('ws/order/<order_id>/', consumers.OrderConsumer.as_asgi()),
]

# websocket_urlpatterns = [
#     path("", ChatConsumer.as_asgi()),
# ]