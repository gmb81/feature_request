from flask_bcrypt import generate_password_hash, check_password_hash
from flask_login import UserMixin
from peewee import *


DATABASE = SqliteDatabase('threes.db')

class User(UserMixin,Model):

    username = CharField(max_length=80, unique=True)
    email = CharField()
    password = CharField()




    @classmethod
    def create_user(cls, username,email, password, admin=False):
        try:
            cls.create(
            username=username,
            email = email,
            password = generate_password_hash(password),
            is_admin=admin)
        except IntegrityError:
            raise ValueError('User already exists')

    class Meta:
        database= DATABASE





class Feature(Model):
    user = ForeignKeyField(
        rel_model=User,
        related_name = 'feature'
    )
    title = CharField(max_length=120)
    description = TextField()
    client = CharField()
    client_priority = IntegerField(unique=True)
    target_date = DateField()
    ticket_url = CharField()
    product_area = CharField()
    percent_complete = IntegerField(null=True, default=0)
    working_ticket = ForeignKeyField(
        rel_model=User,
        related_name='working_ticket',
        null=True
    )

    class Meta:
        database = DATABASE





def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User, Feature], safe=True)
    DATABASE.close()