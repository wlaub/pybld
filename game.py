import os, time, sys
import importlib, inspect
import pickle
from gmap import *

import pdb

WIDTH = 60
HEIGHT = 45

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


def formatStrings(strings, size = 5, width = 10):
    #:((( 
    pass 


def sayBit(data):
    sys.stdout.write(data.upper())
    sys.stdout.flush()

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

def fail(string = "Hmm..."):
    say(string)
    return False

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

def getInter(list1, list2):
    return [x for x in list1 if x in list2]



def _doCmd(obj, cmd):
    for v in obj.verbs:
        if v in cmd:
            getattr(obj, v)(cmd)
            return True
    for v in obj.fancyVerbs.keys():
        if v in cmd:
            getattr(obj, obj.fancyVerbs[v])(cmd)
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

    fancyVerbs = {
    "==>": "_mspa"
    }

    alarms = {}

    def __init__(self):
        self.currRoom = None
        self.flags = {}
        self.rooms = {}
        self.items = {}
        self.lastSave = "default"

    def loadModules(self):
        roomFiles = os.listdir('./rooms')
        items = []
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
                                nItem = mod.__dict__[val](self)
                                items.append(nItem)
                                self.addItem(nItem)
                            except Exception as e:
                                print(e)
                    except Exception as e:
                        pass

        for item in items:
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
        if not item.unique:
            return
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

    def setAlarm(self, delay, func):
        turn = self.flags["turns"]+delay
        if not turn in self.alarms.keys():
            self.alarms[turn] = []
        self.alarms[turn].append(func)

    def tickTurn(self):
        turns = self.getFlag("turns")
        sub = self.getFlag("subTurn")
        hair = self.getFlag("hair")
        sub += 1

        if sub >= hair:
            sub = 0
            turns += 1
            if turns in self.alarms.keys():
                for func in self.alarms[turns]:
                    func()

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
        return True

    def load(self, cmd):
        loadGame = self._saveLoad(cmd, load)
        if loadGame == None:
            say("Failed to load game {}.".format(self.lastSave))
            return False
        self.__dict__.update(loadGame.__dict__)
        say("Loaded gamed {}.".format(self.lastSave))
        return True

       

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
        return True


    def help(self, cmd):
        return fail("there is no one here you can help.")

    def hint(self, cmd):
        return fail("I don't need any hints, but thanks for offering.")

    def exit(self, cmd):
        self.done = True
        return True

    def _mspa(self, cmd):
        return fail("hhhhhhm..")

class Room():
    name = ""
    verbs = ["look", "go", "sit", "stand", "loc"]

    strings = {
    "desc": "It is a room?",
    "closer": "You take a closer look.",
    }

    fancyVerbs={}

    _map = Map()
    defPos = ""

    def __init__(self, game):
        self.items = {}
        self.g = game
        self.pos = self.defPos


    def _getItems(self):
        for item in self.g.items.values():
            if item.loc == self.name:
                self.items[item.name] = item
                item.room = self

    def _flagName(self, name):
        return _flagName(self, name)

    def _makeItemString(self, obscure = False):
        itemStr = "\n"
        for item in self.items.values():
            if item.obscure == obscure:
                itemStr += item.getGround() + " "
        return itemStr

    def _makeLocStr(self):
        posList = self._map.locs.keys()
        if len(posList) == 0:
            return ""
        lines = ["\nLocations are:\n"]
        line = " "*5
        lineCount = 0
        for pos in posList:
            line += pos + " "*(15-len(pos))
            lineCount += 1
            if lineCount == 4:
                lineCount = 0
                lines.append(line)
        if lineCount != 0:
            lines.append(line)
        return '\n'.join(lines)


    def getFlag(self, name):
        return self.g.getFlag(self._flagName(name), self.flags[name])

    def setFlag(self, name, val):
        self.g.flags[self._flagName(name)] = val

    def doCmd(self, cmd):
        for item in self.items.values():
            if item.name.lower() in cmd:
                if _doCmd(item, cmd):
                    return True
        if _doCmd(self, cmd):
             return True
        return False

    def look(self, cmd):
        if "closer" in cmd:
            say(self.strings['closer'])
            say(self._makeItemString(True))
            return True

        say(self.strings['desc'])

        say(self._makeItemString())
        return True

    def loc(self, cmd):
        say("You are {}.".format(self.pos))
        say(self._makeLocStr())
        return True

    def _enterPos(self, pos):
        enter = ""
        eKey = "enter "+pos
        if "enter "+pos in self.strings.keys():
            enter = self.strings[eKey]
        say(enter) 

    def _goEmpty(self):
        return fail("...")

    def _goDir(self, cmd):
        _dir = getDir(cmd)
        if _dir == None:
            return False
        nPos = self._map.go(self.pos, _dir)
        if nPos != None:
            self.pos = nPos
            self._enterPos(nPos)
            return True
        return True

    def _goOther(self, cmd):
        return fail("This is the base room. You cannot leave.")

    def _goSit(self, cmd):
        return fail("You can't walk while sitting!")

    def go(self, cmd):
        if cmd == "go":
            return self._goEmpty()

        if self.g.getFlag("sit") != "not":
            return self._goSit(cmd)

        if self._goDir(cmd):
            return True

        return self._goOther(cmd)


    def sit(self, cmd):
        state = self.g.getFlag("sit", "down")

        direction = getDir(cmd)

        if state != "not":
            if direction == "up":
                return self.sitUp()
            else:
                return fail("You are already sitting {}".format(state))


        if direction == None:
            return say("Sit in what direction?")
        elif direction == "down":
            return self.sitDown()
        elif direction == "left":
            return self.sitLeft()
        elif direction == "right":
            return self.sitRight()
        else:
            return fail("You cannot sit in the direction.")

    def stand(self, cmd):
        state = self.g.getFlag("sit", "down")

        if state == "not":
            return fail("You are already standing.")

        direction = getDir(cmd)
        if direction == None:
            return say("Stand in what direction?")
        elif direction == "up":
            return self.standUp()
        elif direction == "down":
            return self.standDown()
        else:
            return fail("You cannot stand in that direction.")

    def sitUp(self):
        say("You pay more attention to you posture.")
        return True

    def sitDown(self):
        return fail("There is nowhere to sit.")

    def sitLeft(self):
        return fail("You cannot sit in that direction.")

    def sitRight(self):
        return fail("You cannot sit in that direction")

    def standUp(self):
        say("You stand up. You are now standing.")
        self.g.flags["sit"] = "not"
        return True

    def standDown(self):
        say("You chill the fuck out. You are no longer AGGRO.")
        self.g.flags["aggro"] = 0
        return True


class Item():
    name = "item"
    verbs = ["look", "where"]
    fancyVerbs = {}
    takeable = False    #for automatic take command
    dropable = False    #for automatic drop command
    visible = False     #Appears in room description.
    hidden = False      #Does not respond to look, does not appear in inventory
    spawn = True        #Automatically added to room at startup
    obscure = False     #Listed only in the look closer command
    unique = True       #Adds item to global game dictionary
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
            return fail("Hmmmm...")
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
        if self.visible and not self.hidden:
            return self.strings["ground"]
        return ""

    def look(self, cmd):
        if self.hidden:
            return fail()
        say(self.strings["desc"])
        return True

    def where(self, cmd):
        if self.hidden:
            return fail()
        if self.pos != "":
            say(self.pos)
            return True
        return fail()

    def take(self, cmd):
        if self.takeable == False:
            return fail()
        if self.loc == 'inv':
            return fail("You already have the {}.".format(self.name))
        pPos = self.room.pos
        if pPos != None and pPos != self.pos:
            return fail("You can't reach it from here!")
        self._move('inv')
        self.loc = 'inv'
        say(self.strings['take'])
        return True

    def drop(self, cmd):
        say(self.strings['drop'])
        if self.dropable:
            room = self.g.currRoom
            pPos = room.pos
            self.pos = pPos
            self._move(room.name)
            return True
        return False


