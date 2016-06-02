import game, bldgfx
from game import inv, require, standing
import time, sys

class Room(game.Room):
    name = "gameover"

    strings =   { "desc": ""
                , "closer": ""
                }

    sitable = False #Default
   
    defSprite = bldgfx.Sprite('img/gameover', 0, 0, -1)

    addVerbs = []
    rmVerbs = []

    fancyVerbs ={
                }

    defFlags =  {
                }

    def _onOtherEnter(self):
        

