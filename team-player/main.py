#!/usr/bin/env python                                             

# Importing the controllers that will handle                      
# the generation of the pages:                                    
#from controllers import crons,ajax,generate,mainh                 
from controllers import mainh, team, game

# Importing some of Google's AppEngine modules:                   
import webapp2

# This is the main method that maps the URLs                      
# of your application with controller classes.                    
# If a URL is requested that is not listed here,                  
# a 404 error is displayed.                                       

#def main():                                                       
#     application = webapp.WSGIApplication([                        
#         ('/', mainh.MainHandler),                                 
#         ('/crons/5min/', crons.FiveMinHandler),                   
#         ('/crons/1day/', crons.OncePerDayHandler),                
#         ('/ajax/24hours/', ajax.TwentyFourHours),                 
#         ('/ajax/7days/', ajax.SevenDays),                         
#         ('/ajax/30days/', ajax.ThirtyDays),                       
#         ('/generate-test-data/', generate.GenerateTestData)       
#         ],debug=True)                                                 
#     util.run_wsgi_app(application)                                

app = webapp2.WSGIApplication([                        
    ('/', mainh.MainHandler),                                 
    ('/team/(.*)/(.*)', team.TeamHandler),
    ('/game/(.*)/(.*)/(.*)', game.GameHandler),
    ('/admin/(.*)', mainh.AdminHandler),
    ],debug=True)                                                 
