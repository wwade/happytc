#!/usr/bin/env python


#	Script Configuration. Replace these
#	values with your own.
#
#	scriptTitle		Self-explanatory
#
#	fetchURL		This holds the page that is to be
#					fetched from your domain.
#
#	searchString	This setting holds a string that
#					is going to be searched in the
#					fetched page.

import os
from datetime import datetime
from google.appengine.api import users

scriptTitle 	= "Team Player"
fetchURL		= "http://www.google.com/"
searchString	= "Google"

def render_default(d_in=None):
    if d_in == None:
        d_in = {}
    mapper = {
        "title"	: scriptTitle,
        "year"	: datetime.now().strftime("%Y"),
        "domain": fetchURL.replace('http://','').replace('/',''),
        "logout_url": users.create_logout_url("/"),
    }
    for k in mapper.keys():
        if not d_in.has_key(k):
            d_in[k] = mapper[k]
    return d_in

def view_path(filename):
    return os.path.join(os.path.dirname(__file__), '../views', filename)
