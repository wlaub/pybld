import game, bldgfx
from game import inv, require, standing
import time, sys

class Room(game.Room):
    name = "Second Room"

    strings =   { "desc": "You are in a bare room."
                , "closer": "There's nothing else here."
                , "sit": "You had better not..."
                }

    sitable = False
   
#    defSprite = bldgfx.Sprite('img/', 0, 0, -1)

    addVerbs = []

    fancyVerbs ={
                }

    defFlags =  {
                }

    def _onFirstEnter(self):
        game.say("The door slams shut behind you and then vanishes.")



class Chair(game.Item):
    name = "chair"

    takeable =  False
    dropable =  False
    visible  =  True 
    hidden   =  False 
    spawn    =  True  
    obscure  =  False 
    unique   =  True  
    useable  =  False 

    strings = {
        "desc": "The {} pulses with DARK MAGYX.",
        "ground": "There is a {} in the middle of the room.",
        "take": "You'd better not get too close",
    }

    addVerbs = []
    
    fancyVerbs ={
                }

    defFlags =  {
                }    

#    defSprite = bldgfx.Sprite('img/', 0, 0)

    defLoc = 'Second Room'


