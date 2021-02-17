from tortoise.models import Model
from tortoise import fields
from tortoise import Tortoise

class NeosInstance(Model):
    # Defining `id` field is optional, it will be defined automatically
    # if you haven't done it yourself
    id = fields.IntField(pk=True)
    world_name = fields.CharField(max_length=255)

    def __str__(self):
        return self.world_name


class Server(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    # References to other models are defined in format
    # "{app_name}.{model_name}" - where {app_name} is defined in tortoise config
    tournament = fields.ForeignKeyField('models.NeosInstance', related_name='neos_instances')

    def __str__(self):
        return self.name


class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    neos_id = fields.CharField(max_length=255)

    def __str__(self):
        return f"User id={self.id} name={self.name} neos_id={self.neos_id}"

async def init():
    # Here we create a SQLite DB using file "db.sqlite3"
    #  also specify the app name of "models"
    #  which contain models from "app.models"
    await Tortoise.init(
        db_url='sqlite://db.sqlite3',
        modules={'models': ['app.models']}
    )
    # Generate the schema
    await Tortoise.generate_schemas()

