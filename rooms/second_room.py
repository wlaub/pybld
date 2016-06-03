import game, bldgfx
from game import inv, require, standing, needItem
import time, sys

class Room(game.Room):
    name = "Second Room"

    strings =   { "desc": "You are in a bare room lit only by the FBDNG GLOW or DARK MAGYX."
                , "closer": "There's nothing else here."
                , "sit": "You had better not..."
                , "safeSit": "It seems safe enough now. You sit in the chair."
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

    def sit(self, cmd):
        safe = self.items['chair'].getFlag('safe')
        if not safe:
            game.say(self.getString('sit'))
        else:
            game.say(self.getString('safeSit'))
            time.sleep(2) #TODO: same
            game.g.moveRoom('victory')




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

    strings =   { "desc": "The {} pulses with DARK MAGYX."
                , "descSafe": "The {} looks safe now."
                , "ground": "There is a {} in the middle of the room."
                , "take": "You'd better not get too close"
                , "takeSafe": "You can't pick it up. It's too unwieldy."
                }

    addVerbs = []
    
    fancyVerbs ={
                }

    defFlags =  { "safe": False
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
        safe = self.room.items['chair'].getFlag('safe')
        if not safe:
            game.say("You sit in the chair despite your better judgment.")
            time.sleep(2) #TODO: Replace with confirm action
            game.g.moveRoom('gameover')
        else:
            return self.room.sit('sit')


class Darkmagyx(game.Item):
    name = "dark magyx"

    takeable =  False #Default
    dropable =  False #Default
    visible  =  False  #Default
    hidden   =  False  #Default
    spawn    =  True   #Default
    obscure  =  False  #Default
    unique   =  True   #Default
    useable  =  False  #Default

    strings =   { "desc": "The {} pulse and writhe upon the CHAIR."
                , "ground": ""
                , "take": ""
                , "drop": ""
                , "dispel": "The BLACK WIND leaves your INV and passes through the CHAIR. The {} has been D'SPEL!"
                }

    addVerbs = []
    
    fancyVerbs ={ "d'spel": 'dispel'
                }

    defFlags =  {
                }    

    defSprite = bldgfx.Sprite('img/sroom/magyx1.bmi', 0, 19)

    defLoc = 'Second Room'
    defQty = 1

    #require black wind
    @needItem('black wind')
    def dispel(self, cmd):
        chair = self.room.items['chair']
        game.say(self.getString('dispel'))
        game.g.inv.items['black wind']._move('trash')
        chair.strings['desc'] = chair.strings['descSafe']
        chair.strings['take'] = chair.strings['descSafe']
        chair.sprite.change('img/sroom/chair2.bmi') 
        self.room.items['chair'].setFlag('safe', True)
        self._move('trash')
        return True




