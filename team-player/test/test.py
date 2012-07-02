from models import models

from google.appengine.api import mail
from google.appengine.api.users import User
from google.appengine.ext import db
from urllib import unquote

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
        ["Wade Carpenter", WADE, ["+1-604-788-5894"]],
        ["Cher Choi", CHER, ["+1-604-833-2437", "+1-604-395-5293"]],
    ]
    players = [
        ["Non Admin", "wcarpenter@fortinet.com", ["+1-604-420-1297 x 6912"]],
        ["Other One", "wade.carpenter+1@gmail.com",[]],
        ["Other Two", "wade.carpenter+2@gmail.com",[]],
        ["Other Three", "wade.carpenter+3@gmail.com",[]],
    ]

    # Add Admins
    for a in admins:
        ph = []
        for p in a[2]:
            ph.append(db.PhoneNumber(p))
        q = models.Admin.all()
        q.filter("name =",a[0])
        q.filter("user =",User(a[1]))
        admin = q.get()
        if admin == None:
            admin = models.Admin(name=a[0], user=User(a[1]), phone=ph)
            log("Added admin: %s" % repr(a))
        else:
            log("Admin already exists: %s" % repr(a))
        admin.mail = a[1]
        admin.put()


    # Add Regular Players
    for a in players:
        ph = []
        for p in a[2]:
            ph.append(db.PhoneNumber(p))
        q = models.Player.all()
        q.filter("name =",a[0])
        q.filter("mail =",a[1])
        if q.get() == None:
            pl = models.Player(name=a[0], mail=a[1], phone=ph)
            pl.put()
            log("Added player: %s" % repr(a))
        else:
            log("Player already exists: %s" % repr(a))

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
                    add_player_by_mail(team, u[1])
                for u in players:
                    add_player_by_mail(team, u[1])

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
            html("<td>%s</td><td>%s</td><td><a href=\"/team/%s\">%s</a></td>" %
                 (t.name, player.name, tp.uri_id, tp.uri_id))
            html("</tr>")
    html("</table>")
