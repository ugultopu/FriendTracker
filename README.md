# Set Up #

1. [Install Redis](https://redis.io/download) (you can use a package manager for this)
2. Start Redis with `redis-server`
3. `python -m venv FriendTracker-Env`
4. `cd FriendTracker-Env`
5. `source bin/activate`
6. `pip install -r requirements.txt`
7. `git clone git@bitbucket.org:ugultopu/FriendTracker.git`
8. `cd FriendTracker`
9. `./runserver.sh`

You can now make HTTPS connections to `localhost:8443` and HTTP connections to `localhost:8000`.
