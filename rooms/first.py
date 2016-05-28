import game, bldgfx
import time, sys
import traceback

class Room(game.Room):
    name = "First Room"

    strings = {
    "desc": "You are sitting in a room, different from the one I am in. There is a door to the RIGHT.",
    "closer": "You take a closer look. The walls and floor are made out of MATERIALS.ACOUSTIC.002C.COLORS.00.NAME MATERIALS.ACOUSTICS.002C.NAME. The drop ceiling is made of white high-grade asbestos tile. There is a single square flourescent light in the middle of the ceiling. You stare hard at the ceiling for a few minutes to make sure it's not coated in shifting iridescent glyphs. It is not.",
    "enter right": "You are now standing next to the door.",
    "no beans": "There are no bean(s) left in the alpha bnple.",
    "beanup": "You increment the beancount.",
    "beandown": "You decrement the beancount."
    }

   
    _map = game.HalfMap()
    defPos = "left"

    defSprite = bldgfx.Sprite('img/froom/froom.bmi', 0, 0, -1)

    addVerbs = ["beanup","beandown"]

    def beanup(self, cmd):
        if not 'bean' in self.items['left'].keys():
            return game.fail(self.getString("no beans"))
        game.say(self.getString("beanup"))
        self.items['left']['bean'].qty += 1
        return True

    def beandown(self,cmd):
        if not 'bean' in self.items['left'].keys():
            return game.fail(self.getString("no beans"))
        game.say(self.getString("beandown"))
        self.items['left']['bean'].qty -= 1       
        return True 

    def sitDown(self):
        game.say("You sit down on the floor.")
        game.g.flags["sit"] = "down"
        return True


class Bean(game.Item):
    name = "bean"
    unique = False
    takeable = True
    dropable = True
    visible = True
    strings = {
        "desc": "It is a {}",
        "ground": "There are {qty} {}(s) on the ground.",
        "take": "You take a {}.",
        "drop": "You drop a {}."
    }

    defSprite = bldgfx.Sprite('img/froom/beanmd.bmi', 10, 15)

    defLoc = 'First Room'
    defPos = 'left'
    defQty = 5

    def _checkSprite(self):
        if self.qty < 3:
            self.sprite.name = 'img/froom/beansm.bmi'
        elif self.qty < 6:
            self.sprite.name = 'img/froom/beanmd.bmi'
        else:
            self.sprite.name = 'img/froom/beanlg.bmi'


class Door(game.Item):
    name = "door"

    strings = {
        "desc": "It is a mural of a {}",
        "desc2": "It is a normal {}"
    }


    defLoc = "First Room"
    defPos = 'right'

    addVerbs = ["open"]

    defSprite = bldgfx.Sprite('img/froom/door.bmi', 2, 40)


    def look(self, cmd):
        state = game.g.getFlag("text pars'r", 0)
        if state == 0:
            game.say(self.getString("desc"))
        else:
            game.say(self.getString("desc2"))
  
    def open(self, cmd):
        state = game.g.getFlag("text pars'r", 0)
        pos = self.room.pos

        if state ==0:
            return game.fail("It's not a real door.")
        if pos != "right":
            return game.fail("You can't reach the door from here. You are too far left.")
        game.say("You open the door and walk through into the next room. There's no going back now. Hope you didn't miss anything important!")
  
        game.lf()
        game.say("Congratulations! You completed the demo of pybld.\nYour score was: {score}\nYour hair was: {hair}\n Your turns was: {turn}".format(score = game.g.getScore(), hair=game.g.getHair(), turn=game.g.getTurns()))

        #replace with achievements
        game.say("BLACK WINDS obtained: {}/1".format(game.g.hasItem('black wind')))
        game.say("GLYPHS PARS'D: {}/1".format(0))
        game.say("D'LDOS BROK'N: {}/1".format(1 if game.g.items["d'ldo"].broken else 0))
        return True
 
class Glyph(game.Item):
    obscure = True
    visible = True
    name = "glyphs"
    defLoc = "First Room"

    strings = {
        "desc":"They are shifting iridescent {} on the ceiling. You have to stare for a few seconds to see them.",
        "ground": "Oh wait yes it is.",
        "use": "You still don't know what they mean..."
    }

    defPos = ""
    addVerbs = ["use"]

    def use(self, cmd):
       game.say(self.getString('use')) 



class BlackWind(game.Item):
    takeable = True
    dropable = False
    visible = False
    name = "black wind"
    defLoc = "First Room"

    strings = {
        "desc": "It is the {} that blew through you earlier.",
        "take": "You quickly snatch the {} before it can blow away.",
        "take2": "It already got away...",
        "drop": "You try to drop it but it just floats there."
    }

    defPos = 'left'

    addVerbs = ["use"]

    defFlags = {
    "time": -1, 
    "ticks": 0,
    "escape": False,
    }

    timeout = 3

    def _tick(self):
        if self.loc == 'inv':
            return
        t = self.getFlag("ticks")
        if t == 0:
            self.pos = "right"
        else:
            self.hidden = True
            return
        game.g.setAlarm(self.timeout, self._tick)
        self.setFlag("ticks",t+1)


    def take(self, cmd):
        blkTime = self.getFlag("time")
        currTime = game.g.getFlag("turns")
        escape = self.getFlag("escape")
        if blkTime < 0:
            return game.fail("...")
        elif self.hidden:
            return game.fail(self.getString('take2'))
        return game.Item.take(self, cmd)



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
        "use": "The TEXT PARS'R throbs gently in your hands. It seems pleased.",
        "useHint": "The TEXT PARS'R throbs gently in your hands. It seems pleased, but it would like a little more attention.",
        "usePrimed": "The TEXT PARS'R pulse violenty in your hands. It seems XCIT'D."
    }

    defPos = 'left'

    addVerbs = ["use", "caress", "eat"]

    defFlags = {
    "tries": 0,
    "speed": 0
    }

    defSprite = bldgfx.Sprite('img/froom/txt.bmi', 9, 23)

    def eat(self,cmd):
        game.say("Ew, no.")


    speedStr = ["you can't help it.", "you open your mouth as wide as you can.", 
                "and force the text parser inside.", "your throat convulses as you try to resist.",
                "but you swallow anyway.", "it doesn't seem to fit but you keep trying.",
                "eventually it slides down your throat.", "you can feel it throbbing inside you."]


    def take(self, cmd):
        if game.Item.take(self, cmd):
            wind = game.g.items['black wind']
            game.g.setAlarm(wind.timeout, wind._tick)
            blkTime = game.g.getFlag("turns")
            game.g.items['black wind'].setFlag("time", blkTime)
            return True
        return False

    def use(self, cmd):
        if not self._reqInv():
            return False

        tries = self.getFlag("tries")
        speed = self.getFlag("speed")


        if speed == 1:
            game.say(self.getString("usePrimed"))
            return False
        elif speed > 1 and speed < len(self.speedStr)+2:
            game.g.forceCmd("use text pars'r")
            self.setFlag("speed", speed + 1)
            game.say(self.speedStr[speed-2])
        elif speed == len(self.speedStr) +2:
            game.say("You obtained the text pars'r! HP/MP restored.\n")
            time.sleep(1)
            game.sayLine("But you're still ")
            game.spell("h u n g r y", .25)
            game.say("...")
            game.g.flags["text pars'r"] = 1
            self._move("trash")
        else:
            if tries > 0:
                game.say(self.getString('useHint'))
            else:
                game.say(self.getString('use'))
            self.setFlag("tries", tries+1)
            return False
        return True


    def caress(self, cmd):
        if not self._reqInv():
            return False

        speed = self.getFlag("speed")
        if speed < 2:
            game.say("It begins to beat faster.")
            self.setFlag("speed", speed + 1)
            if speed == 1:
                game.say("It is ready.")
            return True
        if speed == 2:
            game.say("It is ready.")
            return False
        return False


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

    addVerbs = ["use"]

    defSprite = bldgfx.Sprite('img/froom/dldo.bmi', 8, 3)

    def __init__(self):
        game.Item.__init__(self)
        self.broken = False

    def look(self, cmd):
        if self.broken:
            game.say(self.strings['descBrk'])
        else:
            game.say(self.strings['desc'])
        return True


    def drop(self,cmd):
        if not game.Item.drop(self, cmd):
            return False
        if not self.broken:
            game.say("It breaks.")
            self.sprite.change('img/froom/dldobrk.bmi')
            self.broken = True
        return True

    def use(self, cmd):
        if not self._reqInv():
            return game.fail()
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
                getattr(game.g, v)(cmd)
            except Exception as e:
                eList = traceback.format_stack()
                eList = eList[:-2]
                eList.extend(traceback.format_tb(sys.exc_info()[2]))
                eList.extend(traceback.format_exception_only(sys.exc_info()[0], sys.exc_info()[1]))

                eStr = "Traceback (most recent call last):\n"
                eStr += "".join(eList)
                eStr = eStr[:-1]
                game.say(eStr)
            return True
        return False



