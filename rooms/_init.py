import game, bldgfx
from game import inv, require, standing, needItem
import time, sys

class Room(game.Room):
    name = "_init"

    strings =   { "desc": "This is not real."
                , "closer": ""
                }

    sitable = False
   
#    defSprite = bldgfx.Sprite('img/', 0, 0, -1)

    addVerbs = []

    fancyVerbs ={
                }

    defFlags =  {
                }

    def _onOtherEnter(self):
        game.g.moveRoom('start')
    

