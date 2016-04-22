import game
import time, sys
import traceback

class Room(game.Room):
    name = "First Room"
    desc = "You are sitting in a room, different from the one I am in. There is a door to the RIGHT."

    flags={
    "pos": "left",
    }

    def go(self, cmd):
        dir = game.getDir(cmd)
        pos = self.getFlag("pos")
        if dir == None:
            game.say("...")
            return

        if self.g.getFlag("sit") != "not":
            game.say("You can't walk while sitting!")
            return

        if dir == "left":
            if pos == "left":
                game.say("You can't go any farther left.")
            else:
                self.setFlag("pos", "left")
                game.say("You walk to the left.")

        elif dir == "right":
           if pos == "right":
               game.say("You can't go any farther right.")
           else:
               self.setFlag("pos", "right")
               game.say("You walk to the right. You are now standing next to the door.")
        else:
            game.say("You can't go in that direction.")


    #Figure out why this doesn't work
    def sitDown(self):
        game.say("You sit down on the floor.")
        self.g.flags["sit"] = "down"



class Door(game.Item):
    name = "door"

    strings = {
        "desc": "It is a mural of a {}",
        "desc2": "It is a normal {}"
    }


    defLoc = "First Room"

    verbs = ["look", "open"]


    def look(self, cmd):
        state = self.g.getFlag("text pars'r", 0)
        if state == 0:
            game.say(self.strings["desc"])
        else:
            game.say(self.strings["desc2"])
  
    def open(self, cmd):
        state = self.g.getFlag("text pars'r", 0)
        pos = self.room.getFlag("pos")

        if state ==0:
            game.say("It's not a real door.")
            return
        if pos != "right":
            game.say("You can't reach the door from here. You are too far left.")
            return
        game.say("You open the door and walk through into the next room. There's no going back now. Hope you didn't miss anything important!")
            

class TextParser(game.Item):
    takeable = True
    dropable = False
    visible = True
    name = "text pars'r"
    defLoc = "First Room"

    strings = {
        "desc": "It looks like a normal {}",
        "ground": "There is a {} on the ground.",
        "take":"You pick up the {}. a BLACK WIND blows through you.",
        "drop":"You cannot.",
    }

    defPos = 'left'

    verbs = ["look", "use", "caress", "take", "drop", "eat"]

    flags = {
    "tries": 0,
    "speed": 0
    }


    def eat(self,cmd):
        game.say("Ew, no.")


    speedStr = ["you can't help it.", "you open your mouth as wide as you can.", 
                "and force the text parser inside.", "your throat convulses as you try to resist.",
                "but you swallow anyway.", "it doesn't seem to fit but you keep trying.",
                "eventually it slides down your throat.", "you can feel it throbbing inside you."]


    def use(self, cmd):
        if not self._reqInv():
            return

        tries = self.getFlag("tries")
        speed = self.getFlag("speed")


        if speed == 1:
            game.say("The TEXT PARS'R pulse violenty in your hands. It seems XCIT'D.")
        elif speed > 1 and speed < len(self.speedStr)+2:
            self.g.forceCmd("use text pars'r")
            self.setFlag("speed", speed + 1)
            game.say(self.speedStr[speed-2])
        elif speed == len(self.speedStr) +2:
            game.say("You obtained the text pars'r! HP/MP restored.\n")
            time.sleep(1)
            game.sayBit("But you're still ")
            game.spell("h u n g r y", .25)
            game.say("...")
            self.g.flags["text pars'r"] = 1
            self._move("trash")
        else:
            game.say("The TEXT PARS'R throbs gently in your hands. It seems pleased.")


    def caress(self, cmd):
        if self._reqInv():
            speed = self.getFlag("speed")
            if speed < 2:
                game.say("It begins to beat faster")
                self.setFlag("speed", speed + 1)
            if speed == 2:
                game.say("It is ready.")


class dldo(game.Item):
    takeable = True
    dropable = True
    visible = True
    name = "d'ldo"
    defLoc = "First Room"

    strings = {
        "desc": "The blocky machine shimmers with r'cane en'rgy. There are four rows of keys bearing stranges glyphs you do not recognize. A scroll of parchment protrudes from the top.",
        "descBrk": "It is a broken {}. It's not much use for anyone.",
        "ground": "There is a {} on the ground.",
        "take":"You pick up the {}.",
        "drop":"You drop the {}.",
        "cmd": "slay",
        "useTry": "You press a few keys at random and then press the large one on the right.",
        "use": "The {} shackes and clatters for a few moments as text appears on the parchment:\n",
        "useBrk": "But nothing happens."
    }

    defPos = 'left'

    verbs = ["look", "take", "drop", "use"]

    def __init__(self, g):
        game.Item.__init__(self, g)
        self.broken = False

    def look(self, cmd):
        if self.broken:
            game.say(self.strings['descBrk'])
        else:
            game.say(self.strings['desc'])


    def drop(self,cmd):
        game.Item.drop(self, cmd)
        if not self.broken:
            game.say("It breaks.")
        self.broken = True
       

    def use(self, cmd):
        if not self._reqInv():
            return
        game.say(self.strings['useTry'])
        if not self.broken:
            game.say(self.strings['use'])
        time.sleep(1)
        if self.broken:
            game.say(self.strings['useBrk'])
        else:
            try:
                fakeCmd = self.strings['cmd']
                v = "defy"
                getattr(self.g, v)(cmd)
            except Exception as e:
                eList = traceback.format_stack()
                eList = eList[:-2]
                eList.extend(traceback.format_tb(sys.exc_info()[2]))
                eList.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))

                eStr = "Traceback (most recent call last):\n"
                eStr += "".join(eList)
                eStr = eStr[:-1]
                game.say(eStr)

