import game, bldgfx
from game import inv, require, standing, needItem
import time, sys

class Room(game.Room):
    name = "victory"

    strings =   { "desc": ""
                , "closer": ""
                }

    sitable = False #Default
   
#    defSprite = bldgfx.Sprite('img/', 0, 0, -1)

    addVerbs = []

    fancyVerbs ={
                }

    defFlags =  {
                }

    def _onOtherEnter(self):
        game.say("Congratulations! You completed the demo of pybld.\nYour score was: {score}\nYour hair was: {hair}\n Your turns was: {turn}".format(score = game.g.getScore(), hair=game.g.getHair(), turn=game.g.getTurns()))

        ach = game.g.getAchievements()
        for line in ach:
            game.say(line)


