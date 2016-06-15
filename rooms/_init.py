import game, bldgfx
from game import inv, require, standing, needItem
import time, sys

class Room(game.Room):
    name = "_init"

    strings =   { "desc": ""
                , "closer": ""
                }

    sitable = False
   
    defSprite = bldgfx.Sprite('img/start/title.bmi', 0, 0, -1, callback=bldgfx.oneshot)

    addVerbs = ["start"]

    fancyVerbs ={
                }

    defFlags =  {
                }

    def start(self, cmd):
        game.g.moveRoom('First Room')
   
    def _onOtherEnter(self):
        #Wait for sprite to finish animating?
        
        pass
