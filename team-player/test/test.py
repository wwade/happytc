from models import models
from models import tz

from datetime import datetime
from datetime import timedelta
from google.appengine.api import mail
from google.appengine.api.users import User
from google.appengine.ext import db
from urllib import quote

_obj = None

def log(msg):
    global _obj
    _obj.response.out.write("%s<br/>\n" % msg)

def html(msg):
    global _obj
    _obj.response.out.write("%s\n" % msg)

def add_player_by_mail(team, mail):
   player_q = models.Player.all()
   player_q.filter("mail = ", mail)
   player = player_q.get()
   if player == None:
       return None
   pk = player.key()
   if pk in team.players:
       return player
   if pk in team.spares:
       return player
   team.players.append(pk)
   return player

def populate(obj):
    global _obj
    _obj = obj
    WADE = "wade.carpenter@gmail.com"
    CHER = "cherchoi@gmail.com"
    admins = [
        ["M", "Wade Carpenter", WADE, ["+1-604-788-5894"]],
        ["F", "Cher Choi", CHER, ["+1-604-833-2437", "+1-604-395-5293"]],
    ]
    players = [
        ["M", "Non Admin", "wcarpenter@fortinet.com", ["+1-604-420-1297 x 6912"]],
        ["M", "Guy One", "wade.carpenter+1@gmail.com",[]],
        ["M", "Guy Two", "wade.carpenter+2@gmail.com",[]],
        ["F", "Girl One", "wade.carpenter+3@gmail.com",[]],
        ["F", "Girl Two", "wade.carpenter+4@gmail.com",[]],
    ]

    # Add Admins
    for a in admins:
        ph = []
        for p in a[3]:
            ph.append(db.PhoneNumber(p))
        q = models.Admin.all()
        q.filter("name =",a[1])
        q.filter("user =",User(a[2]))
        admin = q.get()
        if admin == None:
            admin = models.Admin(gender=a[0], name=a[1], user=User(a[2]), phone=ph)
            log("Added admin: %s" % repr(a))
        else:
            log("Admin already exists: %s" % repr(a))
            admin.refresh()
        admin.gender = a[0]
        admin.mail = a[2]
        admin.put()


    # Add Regular Players
    for a in players:
        ph = []
        for p in a[3]:
            ph.append(db.PhoneNumber(p))
        q = models.Player.all()
        q.filter("name =",a[1])
        q.filter("mail =",a[2])
        if q.get() == None:
            pl = models.Player(gender=a[0], name=a[1], mail=a[2], phone=ph)
            pl.put()
            log("Added player: %s" % repr(a))
        else:
            log("Player already exists: %s" % repr(a))

    # Add games (to all teams)
    games = [
        { "d": [ 2012,  6,  2 ], "t": "6:00 PM", "dur": 180, "info": "Info for game" },
        { "d": [ 2012,  6,  9 ], "t": "6:00 PM", "dur": 180, "info": "Info for game" },
        { "d": [ 2012,  6, 16 ], "t": "6:00 PM", "dur": 180, "info": "Info for game" },
        { "d": [ 2012,  6, 23 ], "t": "6:00 PM", "dur": 180, "info": "Info for game" },
        { "d": [ 2012,  6, 30 ], "t": "6:00 PM", "dur": 180, "info": "Info for game" },
        { "d": [ 2012,  7,  3 ], "t": "6:00 PM", "dur": 180, "info": "MyInfo for game" },
        { "d": [ 2012,  7, 10 ], "t": "6:00 PM", "dur": 180, "info": "Info for game" },
        { "d": [ 2012,  7, 17 ], "t": "6:00 PM", "dur": 180, "info": "Info for game" },
        { "d": [ 2012,  7, 24 ], "t": "6:00 PM", "dur": 180, "info": "Info for game" },
        { "d": [ 2012,  7, 31 ], "t": "6:00 PM", "dur": 180, "info": "Info for game" },
        { "d": [ 2012,  8,  3 ], "t": "6:00 PM", "dur": 180, "info": "Info for game" },
        { "d": [ 2012,  8, 10 ], "t": "6:00 PM", "dur": 180, "info": "Info for game" },
        { "d": [ 2012,  8, 17 ], "t": "6:00 PM", "dur": 180, "info": "Info for game" },
        { "d": [ 2012,  8, 24 ], "t": "6:00 PM", "dur": 180, "info": "Info for game" },
        { "d": [ 2012,  8, 31 ], "t": "6:00 PM", "dur": 180, "info": "Info for game" },
        { "d": [ 2012,  9,  3 ], "t": "6:00 PM", "dur": 180, "info": "Info for game" },
        { "d": [ 2012,  9, 10 ], "t": "6:00 PM", "dur": 180, "info": "Info for game" },
        { "d": [ 2012,  9, 17 ], "t": "6:00 PM", "dur": 180, "info": "Info for game" },
        { "d": [ 2012,  9, 24 ], "t": "6:00 PM", "dur": 180, "info": "Info for game" },
        { "d": [ 2012,  9, 30 ], "t": "6:00 PM", "dur": 180, "info": "Info for game" },
    ]


    # Add Teams
    teams = [
        [ CHER, "Chronic Injury", [WADE, CHER] ],
        [ WADE, "Wade's Team", [WADE] ],
    ]

    for t in teams:
        q = models.Admin.all()
        user = User(t[0])
        q.filter("user = ", user)
        owner = q.get()
        if owner == None:
            log("Can't get owner '%s' for team '%s'" % (user, t[1]))
            continue

        q = models.Team.all()
        q.filter("name = ", t[1])
        q.filter("owner = ", owner)
        team = q.get()
        if team == None:
            team = models.Team(name=t[1], owner=owner)
            team.put()

        for game in games:
            tm = datetime.strptime(game["t"], "%I:%M %p")
            dt = datetime(game["d"][0], game["d"][1], game["d"][2], tm.hour, tm.minute)
            dt = tz.to_utc(dt)
            dt_end = dt + timedelta(minutes=game["dur"])
            log("%s - %s" % (str(dt), str(dt_end)))
            g_q = models.Game.all()
            g_q.filter("team = ", team)
            g_q.filter("start = ", dt)
            g_q.filter("end = ", dt_end)
            gobj = g_q.get()
            if gobj == None:
                gobj = models.Game(start=dt, end=dt_end, team=team, info=game["info"])
            else:
                gobj.info=game["info"]
            gobj.put()

        if team != None:
            if owner.own_teams == None:
                owner.own_teams = []
            if not team.key() in owner.own_teams:
                owner.own_teams.append(team.key())
                owner.put()

            for adm in t[2]:
                aq = models.Admin.all()
                aq.filter("user =", User(adm))
                auser = aq.get()
                if aq == None:
                    continue
                if not auser.key() in team.admins:
                    team.admins.append(auser.key())
                if not team.key() in auser.admin_teams:
                    auser.admin_teams.append(team.key())
                    auser.put()

                for u in admins:
                    add_player_by_mail(team, u[2])
                for u in players:
                    add_player_by_mail(team, u[2])

            team.put()
            log("Added/updated team %s [owner %s <%s>]" % (t[1], owner.name, owner.user.email()))
        else:
            log("Skipped team %s [owner %s <%s>]" % (t[1], owner.name, owner.user.email()))


def get_links(obj):
    global _obj
    _obj = obj

    tq = models.Team.all()
    html("<table><tr><th>Team</th><th>User</th><th>Link</th></tr>")
    for t in tq:
        if len(t.players) == 0:
            continue
        for u in t.players:
            html("<tr>")
            player = models.Player.get(u)
            tid = models.TeamPlayer.gen_uri_id(t, player)
            tp = models.TeamPlayer.find_raw(tid)
            if tp == None:
                tp = models.TeamPlayer(team=t, player=player)
                tp.set_uri_id()
                tp.put()
            link = "/team/" + quote(t.name) + "/" + tp.uri_id;
            html("<td>%s</td><td>%s</td><td><a href=\"%s\">%s</a></td>" %
                 (t.name, player.name, link, tp.uri_id))
            html("</tr>")
    html("</table>")
