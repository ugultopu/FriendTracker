from django.contrib.sessions.backends.db import SessionStore as DBStore
from FriendTrackerApp import models


class SessionStore(DBStore):
    @classmethod
    def get_model_class(cls):
        return models.CustomSession

    def create_model_instance(self, data):
        import pdb
        pdb.set_trace()
        obj = super(SessionStore, self).create_model_instance(data)
        try:
            account_id = int(data.get('_auth_user_id'))
        except (ValueError, TypeError):
            account_id = None
        obj.account_id = account_id
        return obj

    def set_account_id(self, value):
        self['_account_id'] = value


