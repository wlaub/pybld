import os
import importlib, inspect

directions = ["up", "down", "left", "right"]

def say(data):
    print(data.upper())

def getDir(cmd):
    for part in cmd.split(' '):
        if part in directions:
            return part

def _doCmd(obj, cmd):
    for v in obj.verbs:
        if v in cmd:
            getattr(obj, v)(cmd)
            return True
    return False

def _flagName(obj, name):
    return obj.name+"~"+name

class Game():
    rooms = {}
    items = {}
    flags = {}

    baseFlags = {
    "subTurn": 0,
    "turns": 0,
    "score": 0,
    "hair": 1
    }

    force = ""
    done = False

    verbs = ["help", "exit", "hint", "score"]

    currRoom = None


    def loadModules(self):
        roomFiles = os.listdir('./rooms')
        for name in roomFiles:
            modName, modExt = os.path.splitext(name)
            if modExt == '.py' and modName != '__init__':
                print("loading module {}".format(name))
            
                mod = importlib.import_module("rooms."+modName)
                self.addRoom(mod.Room(self))

                for val in dir(mod):
                    try:
                        if Item in inspect.getmro(mod.__dict__[val]):
                            print("Found item")
                            self.addItem(mod.__dict__[val](self))
                    except Exception as e:
                        pass

        for item in self.items.values():
	    room = self.rooms[item.loc]
	    room.items[item.name] = item
	    print("Added item {} to room {}".format(item.name, room.name))
	    item.room = room


        self.currRoom = self.rooms['First Room']
        self.inv = self.rooms['inv']


    def doCmd(self, cmd):
        self.tickTurn()
	if self.inv.doCmd(cmd):
            pass
        elif self.currRoom.doCmd(cmd):
            pass
        elif _doCmd(self, cmd):
            pass
        else:
            say('Hmm...')
        say('')



    def addRoom(self, room):
        if not room.name in self.rooms.keys():
            self.rooms[room.name] = room
        else:
            print("Failed to add duplicate room")
    
    def addItem(self, item):
        if not item.name in self.items.keys():
            self.items[item.name] = item
        else:
            print("Failed to add duplicate item")

    def getFlag(self, name, default = None):
        if name in self.flags.keys():
            return self.flags[name]
	elif name in self.baseFlags.keys():
	    self.flags[name] = self.baseFlags[name]
	    return self.flags[name]
        else:
            return default

    def forceCmd(self, cmd):
        self.force = cmd

    def tickTurn(self):
        turns = self.getFlag("turns")
        sub = self.getFlag("subTurn")
        hair = self.getFlag("hair")
        sub += 1

        if sub >= hair:
            sub = 0
            turns += 1

        self.flags["subTurn"] = sub
        self.flags["turns"] = turns


    def addScore(self, val):
        score = self.getFlag("score")
	self.flags["score"] = score+val

    def score(self, cmd):
        score = self.getFlag("score")
	turns = self.getFlag("turns")
	hair = self.getFlag("hair")
	scoreStr = "SCORE: {}".format(score)
        scoreStr += " "*(15 - len(scoreStr))
        scoreStr += "TURNS: {}".format(turns)
        scoreStr += " "*(30 - len(scoreStr))
        scoreStr+= "HAIR: {}".format(hair)
	say(" "*7 + scoreStr)


    def help(self, cmd):
        say("there is no one here you can help.")

    def hint(self, cmd):
        say("I don't need any hints, but thanks for offering.")

    def exit(self, cmd):
        self.done = True


class Room():
    desc = "It is a room?"
    name = ""
    verbs = ["look", "go", "sit", "stand"]
    items = {}

    def __init__(self, game):
        self.g = game


    def _getItems(self):
        for item in self.g.items.values():
            if item.loc == self.name:
                self.items[item.name] = item
		item.room = self

    def _flagName(self, name):
        return _flagName(self, name)

    def getFlag(self, name):
        return self.g.getFlag(self._flagName(name), self.flags[name])

    def setFlag(self, name, val):
        self.g.flags[self._flagName(name)] = val

    def doCmd(self, cmd):
        for item in self.items.values():
            if item.name in cmd:
                if _doCmd(item, cmd):
                    return True
        if _doCmd(self, cmd):
             return True
        return False

    def look(self, cmd):
        say(self.desc)
        itemStr = "\n"
	for item in self.items.values():
	    itemStr += item.getGround() + " "
        say(itemStr)

    def go(self, cmd):
        say("This is the base room. You cannot leave.")


    def sit(self, cmd):
        state = self.g.getFlag("sit", "down")

        direction = getDir(cmd)

        if state != "not":
            if direction == "up":
                self.sitUp()
            else:
                say("You are already sitting {}".format(state))
            return


        if direction == None:
            say("Sit in what direction?")
        elif direction == "down":
            self.sitDown()
        elif direction == "left":
            self.sitLeft()
        elif direction == "right":
            self.sitRight()
        else:
            say("You cannot sit in the direction.")

    def stand(self, cmd):
        state = self.g.getFlag("sit", "down")

        if state == "not":
            say("You are already standing.")

        direction = getDir(cmd)
        if direction == None:
            say("Stand in what direction?")
        elif direction == "up":
            self.standUp()
        elif direction == "down":
            self.standDown()
        else:
            say("You cannot stand in that direction.")

    def sitUp(self):
        say("You pay more attention to you posture.")

    def sitDown(self):
        say("There is nowhere to sit.")

    def sitLeft(self):
        say("You cannot sit in that direction.")

    def sitRight(self):
        say("You cannot sit in that direction")

    def standUp(self):
        say("You stand up. You are now standing.")
        self.g.flags["sit"] = "not"

    def standDown(self):
        say("You chill the fuck out. You are no longer AGGRO.")
        self.g.flags["aggro"] = 0


class Item():
    desc = "It is ITEM?"
    name = ""
    loc = ""
    verbs = ["look"]
    takeable = False
    visible = False
    groundStr = "There is a {}"
    flags = {}
    room = None
   

    def  __init__(self, game):
        self.g = game
        self.groundStr = self.groundStr.format(self.name)


    def _reqInv(self):
        if self.loc != "inv":
            say("Hmmmm...")
            return False
        return True

    def _move(self, newLoc):
        del self.g.rooms[self.loc].items[self.name]
	nRoom = self.g.rooms[newLoc]
        nRoom.items[self.name] = self
	self.room = nRoom
        self.loc = newLoc

    def _flagName(self, name):
        return _flagName(self, name)

    def getFlag(self, name):
        return self.g.getFlag(self._flagName(name), self.flags[name])

    def setFlag(self, name, val):
        self.g.flags[self._flagName(name)] = val


    def getGround(self ):
        if self.visible:
            return self.groundStr
        return ""

    def look(self, cmd):
        say(self.desc)


