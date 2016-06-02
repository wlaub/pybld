import game, bldgfx
from game import inv, require, standing
import time, sys

class Room(game.Room):
    name = "gameover"

    strings =   { "desc": "You have died. Your score was."
                , "closer": ""
                }

    sitable = False #Default
   
    defSprite = bldgfx.Sprite('img/go/go1.bmi', 0, 0, -1)

    addVerbs = []
    rmVerbs = []

    fancyVerbs ={
                }

    defFlags =  {
                }

    def _onOtherEnter(self):
        self.look("look") 
        game.g.score("score")
        

