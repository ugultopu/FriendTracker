data='{"command": "load"}'
sessionid="$1"
url="https://localhost:8443/location/ops/"
content_type="Content-Type: application/json" # This is optional

curl \
	-k \
	-b "sessionid=$sessionid" \
	-H "$content_type" \
	-d "$data" \
	"$url"

