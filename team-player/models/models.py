#!/usr/bin/env python

from google.appengine.ext import db

class Common(db.Model):
    since = db.DateTimeProperty(auto_now_add=True)

class User(Common, db.Model):
    name = db.StringProperty(required=True)
    mail = db.EmailProperty(required=True)

    user = db.UserProperty()
    phone = db.ListProperty(db.PhoneNumber)

class Player(User):
    teams = db.ListProperty(db.Key)

class Admin(Player, User):
    admin_teams = db.ListProperty(db.Key)

class Team(Common, db.Model):
    name = db.StringProperty(required=True)

    owner = db.ReferenceProperty(Admin, required=True)
    admins = db.ListProperty(db.Key)
