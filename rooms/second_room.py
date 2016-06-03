import game, bldgfx
from game import inv, require, standing
import time, sys

class Room(game.Room):
    name = "Second Room"

    strings =   { "desc": "You are in a bare room lit only by a FBDNG GLOW."
                , "closer": "There's nothing else here."
                , "sit": "You had better not..."
                }

    sitable = False
   
    defSprite = bldgfx.Sprite('img/sroom/room.bmi', 0, 0, -1)

    addVerbs = []

    fancyVerbs ={
                }

    defFlags =  {
                }

    def _onFirstEnter(self):
        game.say("The door slams shut behind you and then vanishes.")
        self._onOtherEnter()


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

    defSprite = bldgfx.Sprite('img/sroom/chair.bmi', 0, 23)

    defLoc = 'Second Room'


class Anyway(game.Item):
    name = "anyway"

    takeable =  False #Default
    dropable =  False #Default
    visible  =  False  #Default
    hidden   =  False  #Default
    spawn    =  True   #Default
    obscure  =  False  #Default
    unique   =  True   #Default
    useable  =  False  #Default

    strings = {
        "desc": "",
        "ground": "",
        "take": "",
        "drop": ""
    }

    addVerbs = ["sit"]
    
    fancyVerbs ={
                }

    defFlags =  {
                }    

    defLoc = 'Second Room'
    defQty = 1

    @standing
    def sit(self, cmd):
        game.say("You sit in the chair despite your better judgment.")
        time.sleep(2) #TODO: Replace with confirm action
        game.g.moveRoom('gameover')




