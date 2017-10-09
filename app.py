#!/usr/bin/env python3
import os
import tornado.ioloop
import tornado.web
import tornado.log

import requests
import json

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

class MainHandler(TemplateHandler):
    def get(self):
      self.set_header(
        'Cache-Control',
        'no-store, no-cache, must-revalidate, max-age=0')
      self.render_template("index.html", {})


    def post (self):

    # get city name
        city = self.get_body_argument('city')
    # lookup the weather
        url = "http://api.openweathermap.org/data/2.5/weather"

        querystring = {"q":city,"APIKEY":"2d9a500b15c2b6ea12cd0298f2df8696",'units':'imperial'}

        headers = {
            'cache-control': "no-cache",
            'postman-token': "078aecaa-358e-d124-4994-e3ff366a0a3a"
            }

        r = requests.request("GET", url, headers=headers, params=querystring)
        r = json.loads(r.text)
    # render the weather data
        self.render_template('results.html',{'response': r})
def make_app():
  return tornado.web.Application([
    (r"/", MainHandler),
    (r"/static/(.*)",
      tornado.web.StaticFileHandler, {'path': 'static'}),
  ], autoreload=True)

if __name__ == "__main__":
  tornado.log.enable_pretty_logging()
  app = make_app()
  app.listen(int(os.environ.get('PORT', '8888')))
  print('localhost started on port 8888')
  tornado.ioloop.IOLoop.current().start()
