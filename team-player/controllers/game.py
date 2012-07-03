from config import config
import webapp2
from google.appengine.ext.webapp import template

class GameHandler(webapp2.RequestHandler):
    def get(self, team_name, team_id, game_id):

        path = config.view_path("game.html")
        self.response.out.write(
            template.render(path, config.render_default({
                "title2": "Edit Game",
            }))
        )
