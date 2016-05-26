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
g = None

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
    say(string)


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

class Bld():
    fancyVerbs = {}
    addVerbs = []
    rmVerbs = []
    defVerbs = []
    name = ''
    strings = {}
    defSprite = None
    defFlags = {}
    flagDec = ''


    def __init__(self):
        self.sprite = self.defSprite
        self.verbs = {}
        verblist = list(self.defVerbs)
        verblist.extend(self.addVerbs)
        self.verbs = {}
        verblist = [x for x in verblist if x not in self.rmVerbs]
        for v in verblist:
            try:
                func = getattr(self, v)
            except:
                print("Plain verb error: {} in Bld {}".format(v, self.name))
            else:
                self.verbs[v] = v
        self.verbs.update(self.fancyVerbs)

    def _checkSprite(self):
        """
        Called on show and hide to change the sprite if it
        needs to change. 
        """
        pass

    def _show(self):
        self._checkSprite()
        if self.sprite == None:
            return
        rend.addSprite(self.sprite)
    
    def _hide(self):
        self._checkSprite()
        if self.sprite == None:
            return
        rend.removeSprite(self.sprite)

    def _flagName(self, name):
        return self.name + self.flagDec + name

    def _getVerbs(self):
        return self.verbs.keys()

    def _doCmd(self, cmd):
        for v in self.verbs.keys():
            if v in cmd:
                result = getattr(self, self.verbs[v])(cmd)
                if result != "pass":
                    return True
        return False

    def getFlag(self, name):
        """
        Retrieves the requested flag from the game flag
        dictionary. Returns the default from defFlags if
        not already set. Returns none if no default.
        """
        default = None
        if name in self.defFlags.keys():
            default = self.defFlags[name]
        return g.getFlag(self._flagName(name), default)
      
    def setFlag(self, name, val):
        """
        Sets the given flag in the game flag dictionary.
        """
        g.setFlag(self._flagName(name), val)

    def getString(self, key, **kwargs):
        """
        Retrieves the descriptive string from strings,
        formats it with name and kwargs, and returns the
        result.
        """
        if key in self.strings.keys():
            base = self.strings[key]
        else:
            return None
        return base.format(self.name.upper(), **kwargs) 

       



class Game(Bld):

    defFlags = {
    "subTurn": 0,
    "turns": 0,
    "score": 0,
    "hair": 1
    }

    force = ""
    done = False

    strings =   { 'fail': 'Hmm...'
                }

    defVerbs = ["debug", "help", "exit", "hint", "score", "save", "load"]

    fancyVerbs = {
    "==>": "_mspa"
    }

    alarms = {}

    def __init__(self):
        global g
        Bld.__init__(self)
        g = self
        self.currRoom = None
        self.flags = {}
        self.rooms = {}
        self.items = {}
        self.lastSave = "default"

    def __getstate__(self):
        return self.currRoom, self.inv, self.flags, self.rooms, self.items, self.lastSave

    def __setstate__(self, state):
        self.currRoom, self.inv, self.flags, self.rooms, self.items, self.lastSave = state
        self.refreshImg()

    def initScreens(self, Interface, Screen):
        """
        Initializes the Interface and Screen objects from
        the given classes, then initalizes the renderer
        from the given screen. Also sets global variables
        for renderer and screen.
        """
        global rend, scr
        self.interface = Interface(self)
        self.screen = Screen()
        self.interface.setScreen(self.screen)
        self.screen.setWindow(self.interface.cmdwin)
       
        scr = self.screen 
        rend = bldgfx.Renderer(self.interface.imgwin)

    def commandLoop(self):
        """
        Runs the game.
        """
        self.interface.commandLoop()

    def loadModules(self):
        """
        Loads rooms from all modules in rooms/*.py. and sets
        inventory to the room named 'inv', which must exist.
        """
        with open("logs/gameload", "w") as f:
            roomFiles = os.listdir('./rooms')
            items = []
            for name in roomFiles:
                modName, modExt = os.path.splitext(name)
                if modExt == '.py' and modName != '__init__':
                    f.write("loading module {}\n".format(name))
                
                    mod = importlib.import_module("rooms."+modName)

                    for val in dir(mod):
                        try:
                            thing = mod.__dict__[val]
                            if Room in inspect.getmro(thing):
                                f.write("Found Room\n")
                                self.addRoom(thing())
                            if Item in inspect.getmro(thing):
                                f.write("Found item\n")
                                try:
                                    nItem = thing()
                                    items.append(nItem)
                                    self.addItem(nItem)
                                except Exception as e:
                                    f.write(str(e)+'\n')
                        except Exception as e:
                            pass

            for item in items:
                room = self.rooms[item.loc]
                room.items[item.pos][item.name] = item
                item.room = room
                f.write("Adding item {} to room {}\n".format(item.name, room.name))

            self.inv = self.rooms['inv']

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


    def refreshImg(self):
        self.currRoom._show()

    def doCmd(self, cmd):
        """
        Evaluates the given command and says the fail string
        if the command isn't currently valid. Order is:
        inv -> room -> game
        """
        lf()
        self.tickTurn()
        if self.inv.doCmd(cmd):
            pass
        elif self.currRoom.doCmd(cmd):
            pass
        elif self._doCmd(cmd):
            pass
        else:
            say(self.getString('fail'))
        self.refreshImg()

    def moveRoom(self, name):
        """
        Changes the current room, refreshes rendering info,
        and calls exit and enter functions.
        """
        if self.currRoom:
            self.currRoom._onLeave()
        self.currRoom = self.rooms[name]
        self.refreshImg()
        self.currRoom._onEnter()

    def hasItem(self, name):
        """
        Checks to see if an item with the given name is in
        the inventory and returns the quantity.
        """
        for pos in self.inv.items.values():
            if name in pos.keys():
                return pos[name].qty
        return 0

    def getVerbs(self):
        """
        Returns a list of all currently valid verbs i.e.
        from the game, the current room, and the inventory.
        This is for autocompletion support.
        """
        verbs = []

        verbs.extend(self._getVerbs())
        verbs.extend(self.inv.getVerbs())
        verbs.extend(self.currRoom.getVerbs())
        return verbs

    def getFlag(self, name, default = None):
        """
        Retrieves the requested flag. If not set, returns
        and sets the value from defFlags. If still not set,
        returns default.
        """
        if name in self.flags.keys():
            return self.flags[name]
        elif name in self.defFlags.keys():
            self.flags[name] = self.defFlags[name]
            return self.flags[name]
        else:
            return default

    def setFlag(self, name, val):
        self.flags[name] = val

    def forceCmd(self, cmd):
        """
        Forces the next command to be the given command.
        """
        self.force = cmd

    def getScore(self):
        return self.getFlag("score")

    def getTurns(self):
        return self.getFlag("turns")
    def setTurns(self, val):
        self.setFlag("turns", val)  
 
    #possibly better to derive the game class? 
    def getHair(self):
        return self.getFlag("hair")

    def setAlarm(self, delay, func, *args, **kwargs):
        """
        Sets an alarm to call the function func after delay
        turns with the given arguments.
        """
        turn = self.getTurns()+delay
        if not turn in self.alarms.keys():
            self.alarms[turn] = []
        self.alarms[turn].append((func, args, kwargs))

    def tickTurn(self):
        """
        Move time forward. In this implementation the turn
        count increments every hair commands.
        Also call any relevant alarm functions for the next
        turn.
        """
        turns = self.getTurns()
        sub = self.getFlag("subTurn")
        hair = self.getHair()
        sub += 1

        if sub >= hair:
            sub = 0
            turns += 1
            if turns in self.alarms.keys():
                for func, args, kwargs in self.alarms[turns]:
                    func(*args, **kwargs)

        self.flags["subTurn"] = sub
        self.setTurns(turns)

    def addScore(self, val):
        """
        Add points to the player's score.
        """
        score = self.getFlag("score")
        self.flags["score"] = score+val

    def _getSaveName(self, cmd):
        """
        Gets save name info from save and load commands.
        """
        saveName = extractSaveName(cmd)
        if saveName == None:
            saveName = self.lastSave
        self.lastSave = saveName

    def save(self, cmd):
        """
        Save the game using the given save filename
        """
        self._getSaveName(cmd)
        save(self, self.lastSave)
        say("Saved gamed as {}.".format(self.lastSave))
        return True

    def load(self, cmd):
        """
        Load the game from the given save file and update
        self from the loaded information.
        """
        self._getSaveName(cmd)
        loadGame = load(self, self.lastSave)
        if loadGame == None:
            say("Failed to load game {}.".format(self.lastSave))
            return False
        self.__dict__.update(loadGame.__dict__)
        say("Loaded gamed {}.".format(self.lastSave))
        return True

    def debug(self, cmd):
        """
        Debug command. Stops rendering and starts pdb, then
        restarts rendering.
        """
        rend.play(False)
        pdb.set_trace()
        rend.play(True)
       

    def score(self, cmd):
        """
        Command to display the player's scoring info.
        """
        score = self.getScore()
        turns = self.getTurns()
        hair = self.getHair()
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
    defVerbs = ["look", "go", "sit", "stand", "loc"]

    strings = {
    "desc": "It is a room?",
    "closer": "You take a closer look.",
    "loc": "You are {loc}."
    }

    defFlags = {}
    flagDec = '~'
    
    _map = Map()
    defPos = ""

    def __init__(self):
        Bld.__init__(self)

        self.items = {}
        self.items[''] = {}
        for pos in self._map.locs.keys():
            self.items[pos] = {}
        self.pos = self.defPos
        self.defFlags['entered'] = False

    def _show(self):
        rend.clear()
        Bld._show(self)
        for pos in self.items.values():
            for item in pos.values():
                item._show()

    def _hide(self):
        rend.clear()

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
        lf()
        self.look("look")

    def _onFirstEnter(self):
        self.setFlag("entered", True)
        self._onOtherEnter()

    def _onLeave(self):
        pass

    def getString(self, key):
        return Bld.getString(self, key, loc=self.pos)

    def getVerbs(self):
        verbs = _getVerbs(self)
        for pos in self.items.values():
            for item in pos.values():
                verbs.extend(item.getVerbs())
        return verbs

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

        if g.getFlag("sit") != "not":
            return self._goSit(cmd)

        if self._goDir(cmd):
            return True

        return self._goOther(cmd)


    def sit(self, cmd):
        state = g.getFlag("sit", "down")

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
        state = g.getFlag("sit", "down")

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
        g.flags["sit"] = "not" #fix this
        return True

    def standDown(self):
        say("You chill the fuck out. You are no longer AGGRO.")
        g.flags["aggro"] = 0 #fix this
        return True


class Item(Bld):
    name = "item"
    defVerbs = ["look", "where", "take", "drop"]
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
    defFlags = {} 
    flagDev = '`'
    defLoc = ""
    defPos = ""
    defQty = 1
    defSprite = None

    def bind(self, name):
        def wrapper(f):
            self.fancyVerbs[name] = f
        return f

    def  __init__(self):
        Bld.__init__(self)
        self.qty = self.defQty
        self.loc = self.defLoc
        self.pos = self.defPos

    def _show(self):
        if self.hidden:
            return
        Bld._show(self)

    def getString(self, key):
        return Bld.getString(self, key, q= self.qty)

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

        nRoom = g.rooms[newLoc]
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
                nItem = self.__class__()
                nItem.qty = 1
                nItem.loc = newLoc
                nItem.room = nRoom
                nRoom.items[nPos][self.name] = nItem 

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
            room = g.currRoom
            pPos = room.pos
            self.pos = pPos
            self._move(room.name)
            return True
        return False


