location='{"command": "save", "latitude": 37.32459787, "longitude": -122.02477367}'
sessionid="$1"
url="https://localhost:8443/location/ops/"
#-H "Content-Type: application/json"
curl -k -b "sessionid=$sessionid" -d "$location" "$url"

