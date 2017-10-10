import models

def forward ():
  models.DB.create_tables([models.Weather])

if __name__ == '__main__':
  forward()
