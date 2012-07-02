from config import config
import webapp2
from google.appengine.ext.webapp import template

from models import tz
from datetime import datetime, timedelta

import json
from models import models

class TeamHandler(webapp2.RequestHandler):
    def json_err(self, status=-1, ctx=""):
        self.response.out.write(json.dumps(
            { 'status': status, 'ctx': ctx }
        ))
    
    def post(self, team_name, team_id):
        tp = models.TeamPlayer.find_by_uri_id(team_id)
        if not tp or team_name != tp.team.name:
            return self.json_err()

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
        tp = models.TeamPlayer.find_by_uri_id(team_id)
        if not tp:
            self.response.out.write("Invalid link.")
            return

        if team_name != tp.team.name:
            self.response.out.write("Invalid link.")
            return

        token = team_id

        games = models.Game.all()
        games.filter("team = ", tp.team)
        games.order("start")
        gamedates = []

        for game in games:
            st = tz.from_utc(game.start)
            val = st.strftime("%a, %b ") + str(st.day)
            g = { 
                "t": val,
                "id": game.key().id(),
            }
            if (len(game.info) > 0):
                g["i"] = game.info
            gamedates.append(g)

        girls = []
        guys = []
        first = True
        for pk in tp.team.players:
            pl = models.Player.get(pk)
            if pk == tp.player.key():
                active = True
            else:
                active = False

            games = models.Game.all()
            games.filter("team = ", tp.team)
            games.order("start")

            row = {
                "obj": pl,
                "active": active,
                "male": pl.is_male(),
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


        path = config.view_path("team.html")
        self.response.out.write(
            template.render(path, config.render_default({
                "title2": "Game Schedule (%s)" % tp.player.name,
                "team": tp.team.name,
                "games": gamedates,
                "players": girls + guys,
                "spares": tp.team.spares,
                "token": token,
            }))
        )
