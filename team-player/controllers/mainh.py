#!/usr/bin/env python

import os
from config import config

import webapp2
from google.appengine.ext.webapp import template
 
import json

from google.appengine.api import users

# This controller handles the
# generation of the front page.

class MainHandler(webapp2.RequestHandler):
    def get(self):
        path = os.path.join(os.path.dirname(__file__), '../views' ,'index.html')
        self.response.out.write(template.render(path, config.render_default({
            "title2": "Schedule",
            "team": "Chronic Injury",
        })))

class AdminHandler(webapp2.RequestHandler):
    def get(self, key):
        path = os.path.join(os.path.dirname(__file__), '../views' ,'admin.html')
        self.response.out.write(template.render(path, config.render_default({
            "title2": "Admin",
            "team": "Chronic Injury",
        })))
