stunnel stunnel/dev_https &
python manage.py runserver

kill_stunnel() {
	kill $stunnel_pid
}

trap kill_stunnel exit stunnel stunnel/dev_https & stunnel_pid=$1
