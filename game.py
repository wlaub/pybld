import os, time, sys
import importlib, inspect
import pickle

directions = ["up", "down", "left", "right"]

def makeSaveName(name):
    return "save/"+name+".bld"

def save(g, filename):
    with open(makeSaveName(filename), "wb") as f:
        pickle.dump(g, f)

def load(g, filename):
    with open(makeSaveName(filename), "rb") as f:
        return pickle.load(f)



def getSaveNames():
    files = os.listdir("save")
    saves = []
    for name in files:
        parts = name.split('.')
        if len(parts) > 1 and parts[1] == 'bld':
            saves.append(name)
    return saves



def sayBit(data):
    sys.stdout.write(data.upper())

def spell(data, delay=.75):
    for c in data:
        sayBit(c)
        time.sleep(delay)

def say(data):
    if data.strip() != "" and data != None:
        sayBit(data)
        sayBit('\n')

def lf():
    sayBit('\n')

def extractSaveName(cmd):
    parts = cmd.split(' ')
    next = False
    for p in parts:
        if next:
            return p
        if p == 'save' or p == 'load':
            next = True
    return None


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

    baseFlags = {
    "subTurn": 0,
    "turns": 0,
    "score": 0,
    "hair": 1
    }

    force = ""
    done = False

    verbs = ["help", "exit", "hint", "score", "save", "load"]

    def __init__(self):
        self.currRoom = None
        self.flags = {}
        self.rooms = {}
        self.items = {}
        self.lastSave = "default"

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
                            try:
                                self.addItem(mod.__dict__[val](self))
                            except Exception as e:
                                print(e)
                    except Exception as e:
                        pass

        for item in self.items.values():
            room = self.rooms[item.loc]
            room.items[item.name] = item
            item.room = room
            print("Adding item {} to room {}".format(item.name, room.name))



        self.currRoom = self.rooms['First Room']
        self.inv = self.rooms['inv']



    def doCmd(self, cmd):
        lf()
        self.tickTurn()
        if self.inv.doCmd(cmd):
            pass
        elif self.currRoom.doCmd(cmd):
            pass
        elif _doCmd(self, cmd):
            pass
        else:
            say('Hmm...')
        lf()
        

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

    def _saveLoad(self, cmd, func):
        saveName = extractSaveName(cmd)
        if saveName == None:
            saveName = self.lastSave
        self.lastSave = saveName
        return func(self, saveName)

        

    def save(self, cmd):
        self._saveLoad(cmd, save)
        say("Saved gamed as {}.".format(self.lastSave))

    def load(self, cmd):
        loadGame = self._saveLoad(cmd, load)
        if loadGame == None:
            say("Failed to load game {}.".format(self.lastSave))
            return
        self.__dict__.update(loadGame.__dict__)
        say("Loaded gamed {}.".format(self.lastSave))
        return loadGame

       

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
    posList = []

    def __init__(self, game):
        self.items = {}
        self.g = game


    def _getItems(self):
        for item in self.g.items.values():
            if item.loc == self.name:
                self.items[item.name] = item
                item.room = self

    def _flagName(self, name):
        return _flagName(self, name)

    def _makeItemString(self):
        itemStr = "\n"
        for item in self.items.values():
            itemStr += item.getGround() + " "
        return itemStr

    def _makeLocStr(self):
        if len(self.posList) == 0:
            return ""
        locStr = "\nLocations are:\n"
        line = " "*5
        lineCount = 0
        for pos in self.posList:
            line += pos + " "*(15-len(pos))
            lineCount += 1
            if lineCount == 4:
                lineCount = 0
                locStr += line+'\n'
        if lineCount != 0:
            locStr += line+'\n'
        return locStr


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

        say(self._makeLocStr())

        say(self._makeItemString())

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
    name = "item"
    verbs = ["look"]
    takeable = False
    dropable = False
    visible = False
    strings = {
        "desc": "It is {}?",
        "ground": "There is a {}",
        "take": "I pick up the {} and put it in my INV.",
        "drop": "You drop the {}."
    }
    room = None
    flags = {} 
    defLoc = ""
    defPos = ""

    def  __init__(self, game):
        self.loc = self.defLoc
        self.pos = self.defPos
        self.g = game
        for key, string in self.strings.iteritems():
            self.strings[key] = string.replace("{}", self.name.upper())


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
            return self.strings["ground"]
        return ""

    def look(self, cmd):
        say(self.strings["desc"])

    def take(self, cmd):
        if self.takeable == False:
            return
        if self.loc == 'inv':
            say("You already have the {}.".format(self.name))
            return
        pPos = self.room.getFlag("pos")
        if pPos != None and pPos != self.pos:
            say("You can't reach it from here!")
            return
        self._move('inv')
        self.loc = 'inv'
        say(self.strings['take'])

    def drop(self, cmd):
        say(self.strings['drop'])
        if self.dropable:
            room = self.g.currRoom
            pPos = room.getFlag("pos")
            self.pos = pPos
            self._move(room.name)






