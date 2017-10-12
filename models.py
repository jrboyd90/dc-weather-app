import sys
import datetime
import os
import peewee
from playhouse.db_url import connect
from playhouse.postgres_ext import JSONField

DB = connect(
  os.environ.get(
    'DATABASE_URL',
    'postgres://postgres:9f1b4792f2f746f5a185de5733f6df5f@dokku-postgres-weather:5432/weather'
  )
)
class BaseModel (peewee.Model):
  class Meta:
    database = DB

class Weather (BaseModel):
  city = peewee.CharField(max_length=60)
  weather_data = JSONField()
  created = peewee.DateTimeField(
              default=datetime.datetime.utcnow)

  def __str__ (self):
    return self.city
