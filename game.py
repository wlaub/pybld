import os, time, sys
import importlib, inspect
from functools import wraps
import pickle
from gmap import *
import iface
import bldgfx

import pdb

WIDTH = 60
HEIGHT = 45

scr = iface.CurseScreen()
rend = None
g = None


def debug():
    rend.play(False)
    pdb.set_trace()


def undebug():
    rend.play(True)
    pass



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

def extractSaveName(cmd):
    """
    Extracts a save file name by returning the first word
    after "save" or "load".
    """
    parts = cmd.split(' ')
    next = False
    for p in parts:
        if next:
            return p
        if p == 'save' or p == 'load':
            next = True
    return None

#Text display functions for saying things

def sayLine(data):
    """
    Say some text without adding a newline at the end. Named
    to be intuitive.
    """
    scr.sayLine(data)

def spell(data, delay=.75):
    """
    Spell some text one character at a time with a delay
    between characters. For special effects.
    """
    scr.spell(data, delay)
    
def lf():
    """
    Linefeed. Just adds a newline.
    """
    scr.lf()

def say(data):
    """
    Say some text with a newline at the end. The main
    function for saything things.
    """
    scr.say(data)

def sayList(items):
    """
    Formats and says a list of strings with some spacing.
    """
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



def fail(string = None):
    """
    For commands that have failed e.g. the player used take
    one something that has a take verb but can't be taken
    yet. Allows a thing print a different fail message than
    the default without
    """
    if string == None:
        string = g.getString('fail')
    say(string)
    return False

def _pass():
    """
    For when a function handles a command but wants to let
    other objects try the command as well. Used with the
    base take verb to allow nonunique items in the inventory
    to not block identical items in the room.
    """
    return "pass"



directions = ["up", "down", "left", "right"]

def getDir(cmd):
    """
    Find and return a valid direction in the given command.
    """
    for part in cmd.split(' '):
        if part in directions:
            return part

def getInter(list1, list2):
    """
    Return the intersection of two lists.
    """
    return [x for x in list1 if x in list2]



def require(matches=[], empty=False, any=False):
    """
    A decorator to make a verb function fail if the
    command doesn't contain any of the valid objects.
    """
    def dec(f):
        @wraps(f)
        def wrapper(self, cmd):
            if self._matchCmd(cmd, matches, empty, any):
                return f(self, cmd)
            else:
                return _pass()
        return wrapper
    return dec


def inv(f):
    """
    A decorator to only calls the function if the object
    is in the player's inventory. Useful for use functions.
    """
    @wraps(f)
    def wrapper(self, cmd):
        result = self._reqInv()
        if result != True:
            return result
        return f(self,cmd)
    return wrapper


class Bld():
    """
    Base class for game objects. Handles verbs, descriptive
    strings, sprites, and flags.
    """
    fancyVerbs = {}
    addVerbs = []
    rmVerbs = []
    defVerbs = []
    name = ''
    strings = {}
    defStrings = {}
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

    def _shortCmd(self, cmd):
        """
        Checks to see if a command doesn't have any objects.
        """
        if len(cmd.split(' ')) == 1:
            return True
        return False

    def _matchCmd(self, cmd, matches=[], empty = False, any = False):
        """
        Checks to see if a command contains one of the words
        in matches. Also checks to see if the command has no
        objects if empty is True. If any is True, returns
        True as long as there is an object.
        """
        if any and len(cmd.split(' ')) > 1:
            return True
        if empty and len(cmd.split(' ')) == 1:
            return True 
        for m in matches:
            if m in cmd:
                return True
        return False

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
        """
        Returns only the objects valid verbs as a list. Used
        in getVerbs.
        """
        return self.verbs.keys()

    def getVerbs(self):
        """
        Should be overridden for anything that needs to give
        more than its own verbs e.g. Room and Game.
        """
        return self._getVerbs()

    def _doCmd(self, cmd):
        for v in self.verbs.keys():
            if v == cmd[:len(v)]:
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

    def getString(self, key):
        """
        Retrieves the descriptive string from strings or
        defStrings, formats it with name and self's
        dictionary, and returns the result.
        """
        if key in self.strings.keys():
            base = self.strings[key]
        elif key in self.defStrings.keys():
            base = self.defStrings[key]
        else:
            return None
        return base.format(self.name.upper(), **self.__dict__) 




class Game(Bld):
    """
    Game class handles loading content, setting up screens,
    scoring, timekeeping, flags, saving, loading, and the
    main game loop.
    """

    defFlags = {
    "subTurn": 0,
    "turns": 0,
    "score": 0,
    "hair": 1
    }

    force = ""
    done = False

    defStrings =   { 'fail': 'Hmm...'
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
                                self._addRoom(thing())
                            if Item in inspect.getmro(thing):
                                f.write("Found item\n")
                                try:
                                    nItem = thing()
                                    items.append(nItem)
                                    self._addItem(nItem)
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

    def _addRoom(self, room):
        if not room.name in self.rooms.keys():
            self.rooms[room.name] = room
        else:
            print("Failed to add duplicate room")
    
    def _addItem(self, item):
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
       
    @require(empty=True)
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
        return fail("There is no one here you can help.")

    def hint(self, cmd):
        return fail("I don't need any hints, but thanks for offering.")

    @require(empty = True)
    def exit(self, cmd):
        self.done = True
        return True

    def _mspa(self, cmd):
        """
        A refrance. Example of fancyVerbs.
        """
        return fail("hhhhhhm..")

class Room(Bld):
    """
    A Room is a distinct location in the game. It contains
    items and sublocations. The current room catches
    commands from the player and handles them or passes
    them to items that can. The inventory is a special room
    that also catches commands and holds items in the
    player's inventory.

    Rooms can be entered and exited and will call the
    functions _onFirstEnter, _onOtherEnter, and _onLeave.

    Rooms presently have some shoddy sit/stand functionality
    and use Maps to let the player move between sublocations.
    Items live in a dictionary as items[pos][name]. This
    should probably change. It may be good to make sublocs
    Be Bld.
    """
    name = ""
    defVerbs = ["look", "go", "sit", "stand", "loc"]

    defStrings = {
    "desc": "It is a room?",
    "closer": "You take a closer look.",
    "loc": "You are {pos}."
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
        """
        Formats a description of items in the room, exluding
        obscure items.
        """
        itemStrings = []
        for pos in self.items.values():
            for item in pos.values():
                if item.obscure == obscure:
                    itemStrings.append( item.getGround() )
        return ' '.join(itemStrings)

    def _sayLocStr(self):
        """
        Formats a list of positions in the room, with no
        relation to topology.
        """
        posList = self._map.locs.keys()
        if len(posList) == 0:
            return ""

        say("\nLocations are:\n")

        sayList(posList)

    def _onEnter(self):
        if self.getFlag('entered'):
            self._onOtherEnter()
        else:
            self.setFlag("entered", True)
            self._onFirstEnter()

    def _onOtherEnter(self):
        """
        Called when the player enters the room any time
        other than the first. Runs the look command by
        by default.
        """
        lf()
        self.look("look")

    def _onFirstEnter(self):
        """
        Called the first time the player enters the room.
        Defaults to _onOtherEnter().
        """
        self._onOtherEnter()

    def _onLeave(self):
        """
        Called when the player leaves the room. Does nothing
        by default.
        """
        pass

    def getVerbs(self):
        verbs = self._getVerbs()
        for pos in self.items.values():
            for item in pos.values():
                verbs.extend(item.getVerbs())
        return verbs

    def doCmd(self, cmd):
        """
        Checks commands on items first, then on self.
        """
        #TODO this maybe needs to be updates to use pass correctly
        for pos in self.items.values():
            for item in pos.values():
                if item.name.lower() in cmd:
                    if item._doCmd(cmd):
                        return True
        if self._doCmd(cmd):
             return True
        return False

    @require(["closer"], True)
    def look(self, cmd):
        """
        Says either the desc string or the closer string,
        then says the list of items in the room from
        _makeItemString()
        """
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
        """
        Says the 'loc' descriptive string then calls
        _sayLocStr()
        """
        say(self.getString("loc"))
        self._sayLocStr()
        return True

    def _enterPos(self, pos):
        """
        Says the enter string for entering the given pos
        if one exists.
        """
        enter = ""
        eKey = "enter "+pos
        if "enter "+pos in self.strings.keys():
            enter = self.getString("enter "+pos)
        sayLine(enter) 

    def _goEmpty(self):
        """
        Called for the go command without a direction of
        any kind.    
        """
        return fail("...")

    def _goDir(self, cmd):
        """
        Extracts a direction from the command and then
        tries to go that direction on the current map.
        If successful, calls _enterPos on the new pos to
        print the valid enter string, then does a linefeed.
        """
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
        """
        Called when the go command is not in a valid
        direction. Would get used for things like using
        "go door" to go through a door or "go away" for
        like a joke or w/e.
        """
        return fail("This is the base room. You cannot leave.")

    def _goSit(self, cmd):
        """
        Called the the player tries to go in a direction
        while sitting.
        """
        return fail("You can't walk while sitting!")

    def go(self, cmd):
        """
        Handles the go verb. Different go functionality
        should be implemented in the appropriate _go*
        functions instead of this one.
        """
        if cmd == "go":
            return self._goEmpty()

        if g.getFlag("sit") != "not":
            return self._goSit(cmd)

        if self._goDir(cmd):
            return True

        return self._goOther(cmd)


    def sit(self, cmd):
        """
        Handles sitting in various directions. Is stupid and
        should be reworked.
        """
        #TODO fix this mess
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
        """
        Same dead as sit. Blam this piece of crap.
        """
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
    """
    Items are things that the player can interact with or
    that can do stuff. They have got a bunch of true/false
    flags for common behaviors.

    By default items cannot be picked up or dropped, are not
    listed in the room look command, are unique, and exist
    when the room is created.

    Hidden items are meant to hold information without being
    directly interactable, but can also be interactable
    without the player having and obvious way to know they
    exist, e.g. the Black Wind item in the demo. They will 
    be drawn if they have a sprite.

    Unique items have a unique name and appear in the game
    objects item list so they can be accessed easily from
    anywhere. Non-unique items are unique in a given pos,
    but can appear in multiple different positions. They
    stack up and have quantity, and can't be accessed except
    through the room and position of a given instance.

    Items that are useable will have the use verb added in
    the constructor automatically, so you had better make
    sure to define a use function and call it use.

    defPos is the item's default position within a room and
    defaults to an empty string.
    """

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
    useable = False     #The item can be used

    defStrings = {   "desc": "It is {}?"
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

    def  __init__(self):
        if self.useable:
            self.addVerbs.append("use")
        Bld.__init__(self)
        self.qty = self.defQty
        self.loc = self.defLoc
        self.pos = self.defPos

    def _reqInv(self):
        """
        For verbs that can only be used on an item in the
        player's inventory. If not in inventory, says
        Hmmmm...
        and returns False.
        """
        if self.loc != "inv":
            return fail("Hmmmm...")
        return True

    def _move(self, newLoc, nPos = None):
        """
        Move the item to a different room and position. If
        no position is given, uses the player's last known
        location in the room. Also handles quantities and
        Item duplication/removal for non-unique items.
        """
        oldRoom = self.room
        oldPos = oldRoom.pos

        if self.unique or self.qty == 1:
            del oldRoom.items[oldPos][self.name] 
        else:
            self.qty -=1

        nRoom = g.rooms[newLoc]
        if nPos == None:
            nPos = nRoom.pos

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
        """
        If the item is visible and not hidden, returns the
        string that identifies the item in a room's look
        command. Defaults to the 'ground' descriptive
        string.
        """
        if self.visible and not self.hidden:
            return self.getString("ground")
        return ""

    def look(self, cmd):
        """
        Says the desc string if the items is not hidden.
        Otherwise fails.
        """
        if self.hidden:
            return fail()
        say(self.getString("desc"))
        return True

    def where(self, cmd):
        """
        Says where the item is if it's not hidden and has
        a position.
        """
        if self.hidden:
            return fail()
        if self.pos != "":
            say(self.pos)
            return True
        return fail()

    def take(self, cmd):
        """
        Takes the item if takeable. If the item is unique
        and in the player's inventory, says the have
        descriptive string. If the item is not unique,
        passes so that identical items in the room can catch
        the command.
        If the item is out of reach fails with message
            You can't reach it from here!
        If the take succeeds, prints the take descriptive
        string.
        """
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
        """
        Drops the item if possible. If the item is not in
        the inventory, passes to let items in the inventory
        catch the command. If the item is hidden, fails.
        Otherise, prints the drop descriptive string and
        if the item is dropable, moves the item to the
        player's current room and position.
        """
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


