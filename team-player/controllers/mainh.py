#!/usr/bin/env python

from config import config
from test import test
import webapp2
from google.appengine.ext.webapp import template
 
# import json

class MainHandler(webapp2.RequestHandler):
    def get(self):
        path = config.view_path("index.html")
        self.response.out.write(template.render(path, config.render_default({
            "title2": "Login Page",
            "team": "Chronic Injury",
        })))

class AdminHandler(webapp2.RequestHandler):
    def get(self, key):
        if key == "populate":
            return test.populate(self)
        elif key == "get_links":
            return test.get_links(self)

        path = config.view_path("admin.html")
        self.response.out.write(template.render(path, config.render_default({
            "title2": "Admin",
            "team": "Chronic Injury",
        })))
