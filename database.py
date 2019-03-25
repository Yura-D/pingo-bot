import os

from peewee import *
from playhouse.db_url import connect


try:
    db = connect(os.environ.get('DATABASE_URL')) # add local sql database
except:
    raise Exception('Please add database variable to environment')


class Message(Model):
    reminder_id = PrimaryKeyField(null=False)
    chat_id = CharField()
    created = DateTimeField()
    content = TextField()
    from_user = CharField()
    to_user = CharField()
    to_user_id = CharField()

    class Meta:
        database = db
        db_table = 'messages'
        ordering = ['-created']


if __name__ == '__main__':
    db.create_tables([Message])

