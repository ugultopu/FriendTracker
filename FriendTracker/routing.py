from channels import include


channel_routing = [
    include('FriendTrackerApp.routing.location_routing', path=r'^/location'),
]

