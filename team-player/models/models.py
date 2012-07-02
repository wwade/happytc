#!/usr/bin/env python

from google.appengine.ext import db
from google.appengine.ext.db import polymodel
from urllib import quote
from hashlib import md5 as str_hash

Salt = "xy1zzzz"

class User(polymodel.PolyModel):
    since = db.DateTimeProperty(auto_now_add=True)
    gender  = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    user = db.UserProperty()
    mail = db.EmailProperty()

    phone = db.ListProperty(db.PhoneNumber)

    def gender_fmt(self):
        if len(self.gender)> 0:
            return self.gender[0].lower()
        else:
            return ""

    def is_male(self):
        if self.gender_fmt()[0] == "m":
            return True
        else:
            return False

    def is_female(self):
        if self.gender_fmt()[0] == "f":
            return True
        else:
            return False

class Player(User):
    pass

class Admin(Player, User):
    admin_teams = db.ListProperty(db.Key)
    own_teams = db.ListProperty(db.Key)

class Team(db.Model):
    since = db.DateTimeProperty(auto_now_add=True)
    name = db.StringProperty(required=True)
    owner = db.ReferenceProperty(Admin, required=True)

    players = db.ListProperty(db.Key)
    spares = db.ListProperty(db.Key)

    admins = db.ListProperty(db.Key)

class TeamPlayer(db.Model):
    team = db.ReferenceProperty(Team, required=True)
    player = db.ReferenceProperty(Player, required=True)
    uri_id = db.StringProperty(default='')

    def set_uri_id(self):
        if self.uri_id != None:
            self.uri_id = self.gen_uri_id(self.team, self.player)

    @staticmethod
    def find_by_uri_id(uri_id):
        return TeamPlayer.find_raw(quote(uri_id))

    @staticmethod
    def find_raw(uri_id):
        tp = TeamPlayer.all()
        tp.filter("uri_id = ", (uri_id))
        m = tp.fetch(2)
        if len(m) == 1:
            return m[0]
        else:
            return None
        

    @staticmethod
    def gen_uri_id(team, player):
        det = Salt
        det = det + str(team.key()) 
        det = det + str(player.key())
        stval = str_hash(det).hexdigest()
        return quote(stval)

class Game(db.Model):
    start = db.DateTimeProperty(required=True)
    end = db.DateTimeProperty(required=True)
    team = db.ReferenceProperty(Team, required=True)
    info = db.StringProperty()

class GameResponse(db.Model):
    when = db.DateTimeProperty(auto_now=True)
    player = db.ReferenceProperty(Player, required=True)
    game = db.ReferenceProperty(Game, required=True)
    status = db.IntegerProperty(required=True)
