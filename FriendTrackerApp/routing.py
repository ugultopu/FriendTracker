from channels import route
from .consumers import location_connect, location_receive, location_send, location_disconnect
from .views import location_operations


location_routing = [
    route('websocket.connect', location_connect),
    route('websocket.receive', location_receive),
    route('websocket.send', location_send),
    route('websocket.disconnect', location_disconnect),
]

