#!/usr/bin/env python3
import os
import tornado.ioloop
import tornado.web
import tornado.log
import datetime
import requests
import json
import re
import urllib


from models import Weather

from jinja2 import \
  Environment, PackageLoader, select_autoescape

ENV = Environment(
  loader=PackageLoader('weather', 'templates'),
  autoescape=select_autoescape(['html', 'xml'])
)

class TemplateHandler(tornado.web.RequestHandler):
  def render_template (self, tpl, context):
    template = ENV.get_template(tpl)
    self.write(template.render(**context))

# function for calling API
def retrieve_api_data(city):
    url = "http://api.openweathermap.org/data/2.5/weather"
    querystring = {"q":city,"APIKEY":"2d9a500b15c2b6ea12cd0298f2df8696",'units':'imperial'}
    headers = {
        'cache-control': "no-cache",
        'postman-token': "078aecaa-358e-d124-4994-e3ff366a0a3a"
        }

    r = requests.request("GET", url, headers=headers, params=querystring)
    weatherdata = Weather.create(city=city,
    weather_data = r.json())
    return weatherdata

class MainHandler(TemplateHandler):
    def get(self):
      self.set_header(
        'Cache-Control',
        'no-store, no-cache, must-revalidate, max-age=0')
      self.render_template("index.html", {})


    def post(self):

        # get city name
        city = self.get_body_argument('city')
        city = city.title()
        old = datetime.datetime.utcnow() - datetime.timedelta(minutes=15)

        # look and see if city is in database within last 15mins
        try:
            weatherdata = Weather.select().where(Weather.city == city).where(Weather.created >= old).get()

        # if not, perform API call to get data and create table with new info
        except:
            weatherdata = retrieve_api_data(city)

        # render template with json info
        template = ENV.get_template('results.html')
        self.write(template.render({'response': weatherdata.weather_data}))

#class for finding location of client
class LocationHandler (TemplateHandler):
    def post(self):
        x_real_ip = self.request.headers.get("X-Forwarded-For")
        remote_ip = x_real_ip or self.request.remote_ip
        url = f'http://ipinfo.io/{remote_ip}/json'
        if remote_ip.startswith(('192.', '127.', '10.')):
            url = 'http://ipinfo.io/json'

        # remote_ip = self.request.headers.get('X-Forwarded-For', self.request.headers.get('X-Real-Ip', self.request.remote_ip))

        print('this is your ip' + remote_ip)

        response = urllib.request.urlopen(url)

        data = json.load(response)

        city = data['city']
        weatherdata = retrieve_api_data(city)
        template = ENV.get_template('results.html')
        self.write(template.render({'response': weatherdata.weather_data}))

def make_app():
  return tornado.web.Application([
    (r"/", MainHandler),
    (r"/location", LocationHandler),
    (r"/static/(.*)",
      tornado.web.StaticFileHandler, {'path': 'static'}),
  ], autoreload=True)

if __name__ == "__main__":
  tornado.log.enable_pretty_logging()
  app = make_app()
  app.listen(int(os.environ.get('PORT', '8888')))
  print('localhost started on port 8888')
  tornado.ioloop.IOLoop.current().start()
