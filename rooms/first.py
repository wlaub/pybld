import game
import time

class Room(game.Room):
    name = "First Room"
    desc = "You are sitting in a room, different from the one I am in. There is a door to the RIGHT."

    flags={
    "pos": "left"
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
    desc = "It is mural of a door."
    desc2 = "It is a normal door."

    verbs = ["look", "open"]

    def __init__(self, g):
        game.Item.__init__(self, g)
        self.loc = "First Room"

    def look(self, cmd):
        state = self.g.getFlag("text pars'r", 0)
        if state == 0:
            game.say(self.desc)
        else:
            game.say(self.desc2)
  
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
    visible = True
    name = "text pars'r"
    desc = "It looks like a normal TEXT PARS'R"
    groundStr = "There is a {} on the ground."

    verbs = ["look", "use", "caress", "take", "drop", "eat"]

    flags = {
    "tries": 0,
    "speed": 0
    }

    def __init__(self, g):
        game.Item.__init__(self, g)
        self.loc = "First Room"

    def eat(self,cmd):
        game.say("Ew, no.")

    def take(self, cmd):
        if self.loc == 'inv':
            game.say("You already have the text pars'r.")
        self._move('inv')
        self.loc = 'inv'
        game.say("You pick up the TEXT PARS'R. A BLACK WIND blows through you.")


    def drop(self, cmd):
        game.say("You cannot.")

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
            time.sleep(1.5)
            game.say("But you're still h u n g r y...")
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

