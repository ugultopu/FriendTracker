from django.core.management.base import BaseCommand, CommandError
from FriendTrackerApp.models import User

class Command(BaseCommand):
    help = 'Populates the data base with example values'

    def handle(self, *args, **options):
        User.objects.create_user('a', 'a@a.com', 'a', first_name='a', last_name='a')
        User.objects.create_user('b', 'b@b.com', 'b', first_name='b', last_name='b')
        User.objects.create_user('c', 'c@c.com', 'c', first_name='c', last_name='c')
        User.objects.create_user('d', 'd@d.com', 'd', first_name='d', last_name='d')
        User.objects.create_user('e', 'e@e.com', 'e', first_name='e', last_name='e')
        User.objects.create_user('f', 'f@f.com', 'f', first_name='f', last_name='f')


