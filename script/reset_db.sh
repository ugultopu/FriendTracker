rm -rf FriendTrackerApp/migrations
rm db.sqlite3 dump.rdb
python manage.py migrate && \
python manage.py makemigrations FriendTrackerApp && \
python manage.py migrate
