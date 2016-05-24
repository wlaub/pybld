import os, time, sys
import importlib, inspect
import pickle
from gmap import *
import iface
import bldgfx

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

scr = iface.CurseScreen()
rend = None


def sayLine(data):
    scr.sayLine(data)

def spell(data, delay=.75):
    scr.spell(data, delay)
    
def lf():
    scr.lf()

def say(data):
    scr.say(data)

def fail(string = "Hmm..."):
    say(string)
    return False

def sayList(items):
    xpos = 0
    string = "         "
    for item in items:
        string += item
        xpos += 1
        if xpos == 4:
            xpos = 0
            string += "\n"
        else:
            string += " "*(15-len(item))
    game.say(string)


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

def _pass():
    return "pass"

"""
def _doCmd(obj, cmd):
    for v in obj.verbs:
        if v in cmd:
            result = getattr(obj, v)(cmd)
            if result != "pass":
                return True
    for v in obj.fancyVerbs.keys():
        if v in cmd:
            result = getattr(obj, obj.fancyVerbs[v])(cmd)
            if result != "pass":
                return True
    return False

def _show(obj):
    global rend
    obj._checkSprite()
    if obj.sprite == None:
        return
    rend.addSprite(obj.sprite)

def _hide(obj):
    global rend
    obj._checkSprite()
    if obj.sprite == None:
        return
    rend.removeSprite(obj.sprite)

def _getVerbs(obj):
    result = []
    result.extend(obj.verbs)
    result.extend(obj.fancyVerbs)
    return result

def _flagName(obj, name):
    return obj.name+"~"+name
"""

class Bld():
    verbs = []
    fancyVerbs = {}
    name = ''
    strings = {}
    defSprite = None

    def __init__(self, game):
        self.g = game
        self.sprite = self.defSprite
 
    def _checkSprite(self):
        pass

    def _show(self):
        self._checkSprite()
        if self.sprite == None:
            return
        self.g.rend.addSprite(self.sprite)
    
    def _hide(self):
        self._checkSprite()
        if self.sprite == None:
            return
        self.g.rend.removeSprite(self.sprite)

    def _flagName(self, name):
        return self.name + "~" + name

    def _getVerbs(self):
        result = []
        result.extend(self.verbs)
        result.extend(self.fancyVerbs)
        return result

    def _doCmd(self, cmd):
        for v in self.verbs:
            if v in cmd:
                result = getattr(self, v)(cmd)
                if result != "pass":
                    return True
        for v in self.fancyVerbs.keys():
            if v in cmd:
                result = getattr(self, self.fancyVerbs[v])(cmd)
                if result != "pass":
                    return True
        return False

      


class Game(Bld):

    baseFlags = {
    "subTurn": 0,
    "turns": 0,
    "score": 0,
    "hair": 1
    }

    force = ""
    done = False

    verbs = ["debug", "help", "exit", "hint", "score", "save", "load"]

    fancyVerbs = {
    "==>": "_mspa"
    }

    alarms = {}

    def __init__(self):
        Bld.__init__(self, self)

        self.currRoom = None
        self.flags = {}
        self.rooms = {}
        self.items = {}
        self.lastSave = "default"

    def __getstate__(self):
        return self.currRoom, self.flags, self.rooms, self.items, self.lastSave

    def __setstate__(self, state):
        self.currRoom, self.flags, self.rooms, self.items, self.lastSave = state
#        self.refreshImg()

    def _checkSprite(self):
        pass 

    def initScreens(self, Interface, Screen):
        self.interface = Interface(self)
        self.screen = Screen()
        self.interface.setScreen(self.screen)
        self.screen.setWindow(self.interface.cmdwin)

        self.rend = bldgfx.Renderer(self.interface.imgwin)
        self.rend.play(False)


    def loadModules(self):
        roomFiles = os.listdir('./rooms')
        items = []
        for name in roomFiles:
            modName, modExt = os.path.splitext(name)
            if modExt == '.py' and modName != '__init__':
                print("loading module {}".format(name))
            
                mod = importlib.import_module("rooms."+modName)
#                self.addRoom(mod.Room(self, rend))

                for val in dir(mod):
                    try:
                        thing = mod.__dict__[val]
                        if Room in inspect.getmro(thing):
                            print("Found Room")
                            self.addRoom(thing(self))
                        if Item in inspect.getmro(thing):
                            print("Found item")
                            try:
                                nItem = thing(self)
                                items.append(nItem)
                                self.addItem(nItem)
                            except Exception as e:
                                print(e)
                    except Exception as e:
                        pass

        for item in items:
            room = self.rooms[item.loc]
            room.items[item.pos][item.name] = item
            item.room = room
            print("Adding item {} to room {}".format(item.name, room.name))

        self.inv = self.rooms['inv']

    def refreshImg(self):
        self.currRoom._show()

    def doCmd(self, cmd):
        lf()
        self.tickTurn()
        if self.inv.doCmd(cmd):
            pass
        elif self.currRoom.doCmd(cmd):
            pass
        elif self._doCmd(cmd):
            pass
        else:
            say('Hmm...')
        self.refreshImg()

    def moveRoom(self, name):
        if self.currRoom:
            self.currRoom._onLeave()
        self.currRoom = self.rooms[name]
        self.refreshImg()
        self.currRoom._onEnter()

    def hasItem(self, name):
        for pos in self.inv.items.values():
            if name in pos.keys():
                return pos[name].qty
        return 0

    def getVerbs(self):
        verbs = []

        verbs.extend(_getVerbs(self))
        verbs.extend(self.inv.getVerbs())
        verbs.extend(self.currRoom.getVerbs())
        # Making lists of verbs for autocompletion
        return verbs

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

    def getScore(self):
        return self.getFlag("score")

    def getTurns(self):
        return self.getFlag("turns")
    
    def getHair(self):
        return self.getFlag("hair")

    def setAlarm(self, delay, func):
        turn = self.getFlag("turns")+delay
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
        loadGame.rend = self.rend
        self.__dict__.update(loadGame.__dict__)
        say("Loaded gamed {}.".format(self.lastSave))
        return True

    def debug(self, cmd):
        pdb.set_trace()
       

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

class Room(Bld):
    name = ""
    verbs = ["look", "go", "sit", "stand", "loc"]

    strings = {
    "desc": "It is a room?",
    "closer": "You take a closer look.",
    "loc": "You are {loc}."
    }

    flags = {}
    
    _map = Map()
    defPos = ""

    def __init__(self, game):
        Bld.__init__(self, game)

        self.items = {}
        self.items[''] = {}
        for pos in self._map.locs.keys():
            self.items[pos] = {}
        self.pos = self.defPos
        self.flags['entered'] = False


    def _show(self):
        self.g.rend.clear()
        Bld._show(self)
        for pos in self.items.values():
            for item in pos.values():
                item._show()

    def _hide():
        self.g.rend.clear()

    def _checkSprite(self):
        pass

    def _makeItemString(self, obscure = False):
        itemStrings = []
        for pos in self.items.values():
            for item in pos.values():
                if item.obscure == obscure:
                    itemStrings.append( item.getGround() )
        return ' '.join(itemStrings)

    def _makeLocStr(self):
        posList = self._map.locs.keys()
        if len(posList) == 0:
            return ""

        say("\nLocations are:\n")

        sayList(posList)

    def _onEnter(self):
        if self.getFlag('entered'):
            self._onOtherEnter()
        else:
            self._onFirstEnter()

    def _onOtherEnter(self):
#        return
        lf()
        self.look("look")

    def _onFirstEnter(self):
        self.setFlag("entered", True)
        self._onOtherEnter()

    def _onLeave(self):
        pass

    def getString(self, key):
        if key in self.strings.keys():
            base = self.strings[key]
        elif key in Room.strings.keys():
            base = Room.strings[key]
        return base.format(self.name.upper(), loc=self.pos) 

    def getVerbs(self):
        verbs = _getVerbs(self)
        for pos in self.items.values():
            for item in pos.values():
                verbs.extend(item.getVerbs())
        return verbs

    def getFlag(self, name):
        return self.g.getFlag(self._flagName(name), self.flags[name])

    def setFlag(self, name, val):
        self.g.flags[self._flagName(name)] = val

    def doCmd(self, cmd):
        for pos in self.items.values():
            for item in pos.values():
                if item.name.lower() in cmd:
                    if item._doCmd(cmd):
                        return True
        if self._doCmd(cmd):
             return True
        return False

    def look(self, cmd):
        if "closer" in cmd:
            desc = self.getString('closer')
            items = self._makeItemString(True)
        else:
            desc = self.getString('desc')
            items = self._makeItemString()
    
        say(desc)
        if items != "":
            lf()
            say(items)

        return True

    def loc(self, cmd):
        say(self.getString("loc"))
        self._makeLocStr()
        return True

    def _enterPos(self, pos):
        enter = ""
        eKey = "enter "+pos
        if "enter "+pos in self.strings.keys():
            enter = self.getString("enter "+pos)
        sayLine(enter) 

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
            lf()
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


class Item(Bld):
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

    strings = {   "desc": "It is {}?"
                , "ground": "There is a {}"
                , "take": "I pick up the {} and put it in my INV."
                , "have": "You already have the {}."
                , "drop": "You drop the {}."
                }
    room = None
    flags = {} 
    defLoc = ""
    defPos = ""
    defQty = 1
    defSprite = None

    def bind(self, name):
        def wrapper(f):
            self.fancyVerbs[name] = f
        return f

    def  __init__(self, game):
        Bld.__init__(self, game)
        self.qty = self.defQty
        self.loc = self.defLoc
        self.pos = self.defPos

        for key, string in self.strings.iteritems():
            string = string.replace("{}", self.name.upper())
            self.strings[key] = string

    def _show(self):
        if self.hidden:
            return
        Bld._show(self)

    def _checkSprite(self):
        pass

    def getString(self, key):
        if key in self.strings.keys():
            base = self.strings[key]
        elif key in Item.strings.keys():
            base = Item.strings[key]
        return base.format(self.name.upper(), q = self.qty) 

    def getVerbs(self):
        return _getVerbs(self)


    def _reqInv(self):
        if self.loc != "inv":
            return fail("Hmmmm...")
        return True

    def _move(self, newLoc):
        oldRoom = self.room
        oldPos = oldRoom.pos

        ####Change for qtys
        if self.unique or self.qty == 1:
            del oldRoom.items[oldPos][self.name] 
        else:
            self.qty -=1

        nRoom = self.g.rooms[newLoc]
        nPos = nRoom.pos

        ####Change for qtys

        if self.unique:
            nRoom.items[nPos][self.name] = self
            self.room = nRoom
            self.loc = newLoc
        else:
            if self.name in nRoom.items[nPos].keys():
                nRoom.items[nPos][self.name].qty += 1
            else:
                nItem = self.__class__(self.g)
                nItem.qty = 1
                nItem.loc = newLoc
                nItem.room = nRoom
                nRoom.items[nPos][self.name] = nItem 

#        self.g.refreshImg()

    def getFlag(self, name):
        return self.g.getFlag(self._flagName(name), self.flags[name])

    def setFlag(self, name, val):
        self.g.flags[self._flagName(name)] = val


    def getGround(self ):
        if self.visible and not self.hidden:
            return self.getString("ground")
        return ""

    def look(self, cmd):
        if self.hidden:
            return fail()
        say(self.getString("desc"))
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
            if not self.unique:
                return _pass()
            return fail(self.getString("have"))
        pPos = self.room.pos
        if pPos != None and pPos != self.pos:
            return fail("You can't reach it from here!")
        self._move('inv')
        say(self.getString('take'))
        return True

    def drop(self, cmd):
        if self.loc != 'inv':
            return _pass()
        if self.hidden:
            return fail()
        say(self.getString('drop'))
        if self.dropable:
            room = self.g.currRoom
            pPos = room.pos
            self.pos = pPos
            self._move(room.name)
            return True
        return False


