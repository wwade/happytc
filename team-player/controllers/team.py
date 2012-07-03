from config import config
import webapp2
from google.appengine.ext.webapp import template

from models import tz
from datetime import datetime, timedelta

import json
from models import models

from google.appengine.api import memcache

from hashlib import md5

class TeamHandler(webapp2.RequestHandler):
    def json_err(self, status=-1, ctx=""):
        self.response.out.write(json.dumps(
            { 'status': status, 'ctx': ctx }
        ))
    
    def post(self, team_name, team_id):
        tp = models.TeamPlayer.find_by_uri_id(team_id)
        if not tp or team_name != tp.team.name:
            return self.json_err()

        plcc = "tp_%s_%s" % (tp.team.key(), tp.player.key())
        memcache.delete(plcc)

        try:
            game = models.Game.get_by_id(int(self.request.POST['id']))
            val = int(self.request.POST['val'])
        except:
            return self.json_err()

        if game == None:
            return self.json_err()

        if game.team.key() != tp.team.key():
            return self.json_err(-2, "<br/>[%s]<br/>[%s]" % (game.team.key(), tp.team.key()))

        gr_q  = models.GameResponse.all()
        gr_q.filter("game = ", game)
        gr_q.filter("player = ", tp.player)
        gmr = gr_q.get()
        if gmr == None:
            gmr = models.GameResponse(player=tp.player,
                                      game=game,
                                      status=val)
        gmr.status = val
        gmr.put()

        gr_q  = models.GameResponse.all()
        gr_q.filter("game = ", game)

        male = {}
        female = {}
        for gr in gr_q:
            if gr.player.is_male():
                if not male.has_key(gr.status):
                    male[gr.status] = 0
                male[gr.status] = male[gr.status] + 1
            else:
                if not female.has_key(gr.status):
                    female[gr.status] = 0
                female[gr.status] = female[gr.status] + 1

        upd = datetime.now()
        when = tz.from_utc(upd)

        val = self.request.POST['val']
        resp = {
            "status": 0,
            "val": val,
            "since": "updated " + when.strftime("%x %X"),
            "gameid": game.key().id(),
            "male": male,
            "female": female,
        }
        self.response.out.write(json.dumps(resp))

        
    def get(self, team_name, team_id):
        log = []
        tp = models.TeamPlayer.find_by_uri_id(team_id)
        if not tp:
            self.response.out.write("Invalid link.")
            return

        if team_name != tp.team.name:
            self.response.out.write("Invalid link.")
            return

        now = datetime.now()
        th_key = "gd_%s" % tp.team.key()
        cached = memcache.get(th_key)
        if cached != None:
            if now >= cached['until']:
                memcache.delete(th_key)
                cached = None

        if cached != None:
            md = cached["md"]
            gamedates = cached["gd"]
            log.append("cached gd %s" % th_key)
        else:
            games = models.Game.all()
            games.filter("team = ", tp.team)
            games.filter("start >= ", now)
            games.order("start")
            gamedates = []
            until = None

            m = md5()
            for game in games:
                if until == None and game.start > now:
                    until = game.start
                st = tz.from_utc(game.start)
                val = st.strftime("%a, %b ") + str(st.day)
                g = { 
                    "t": val,
                    "id": game.key().id(),
                }
                if (len(game.info) > 0):
                    g["i"] = game.info
                gamedates.append(g)
                game.hash(m)
            md = m.digest()
            if until != None:
                obj = {
                    "until": until,
                    "md": md,
                    "gd": gamedates,
                }
                age_limit = (until - now)
                memcache.set(th_key, obj, age_limit.seconds)

        girls = []
        guys = []
        first = True
        for pk in tp.team.players:
            pl = models.Player.find_by_key(pk)
            if pk == tp.player.key():
                active = True
            else:
                active = False

            plcc = "tp_%s_%s" % (tp.team.key(), pk)
            pr = memcache.get(plcc)
            if pr != None:
                if not pr.has_key("md") or pr["md"] != md:
                    memcache.delete(plcc)
                else:
                    pr["active"] = active
                    if pr.has_key("male") and pr["male"]:
                        guys.append(pr)
                    else:
                        girls.append(pr)
                    log.append("cached tp %s" % plcc)
                    continue

            games = models.Game.all()
            games.filter("team = ", tp.team)
            games.filter("start >= ", now)
            games.order("start")

            male = pl.is_male()
            if male:
                gender = "male"
            else:
                gender = "female"
            row = {
                "obj": pl,
                "active": active,
                "male": male,
            }
            row_games = []
            idx = 0
            for game in games:
                gr = models.GameResponse.all()
                gr.filter("player = ", pl)
                gr.filter("game = ", game)
                one = gr.get()
                gmr = {}
                if one == None:
                    gmr["v"] = 0
                    gmr["t"] = ""
                else:
                    gmr["v"] = one.status
                    when = tz.from_utc(one.when)
                    gmr["t"] = "updated " + when.strftime("%x %X")
                gmr["id"] = str(game.key().id())
                idx = idx + 1
                row_games.append(gmr)
            row["games"] = row_games
            if pl.is_male():
                guys.append(row)
            else:
                girls.append(row)
            row["md"] = md
            memcache.set(plcc, row)

        path = config.view_path("team.html")
        self.response.out.write(
            template.render(path, config.render_default({
                "title2": "Game Schedule (%s)" % tp.player.name,
                "team": tp.team.name,
                "games": gamedates,
                "players": girls + guys,
                "spares": tp.team.spares,
                "log": log,
            }))
        )
