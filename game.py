import os, time, sys
import importlib, inspect
from functools import wraps
import pickle
from gmap import *
import iface
import bldgfx
import achieve

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
        if len(parts) > 1 and parts[-1] == 'bld':
            saves.append('.'.join(parts[:-1]))
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
    
def lf(num = 1):
    """
    Linefeed. Just adds a newline.
    """
    scr.lf(num)

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


def confirm(text = None):
    """
    Prompt the player for input and return True of False for
    y/n. Default is
    ARE YOU SURE? Y/N
    """
    if text != None:
       return g.interface.getConfirm(text) 
    return g.interface.getConfirm()

def wait(text = None):
    """
    Print some text and wait for the player to press a key
    to continue. Default is 
    (CONTINUE)
    """
    if text != None:
        return g.interface.getPause(text)
    return g.interface.getPause()

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


def needItem(name, qty=1):
    """
    Decorator to require that the player has at least qty
    of the specified item in inv.
    """
    def dec(f):
        @wraps(f)
        def wrapper(self, cmd):
            result = g.hasItem(name)
            if result >= qty:
                return f(self,cmd)
            return fail()
        return wrapper
    return dec


def standing(f):
    """
    A decorator to only calls the function if the player is
    standing and fails otherwise.
    """
    @wraps(f)
    def wrapper(self, cmd):
        if g.getFlag('sit'):
            return fail(g.currRoom.getString("sitFail"))
        return f(self,cmd)
    return wrapper


class Achievement():
    """
    An achievement with a desc and length. Displays as
    [DESC]: X/Y
    where x is the player's progress and y is the total
    possible progress. A single-event achievement will have
    length of 0 e.g.
    BLACK WINDS ACQUIRED: 0/1
    """

    def __init__(self, desc, length = 1):
        self.desc = desc.upper()
        self.length = length
        self.qty = 0

    def give(self, qty = 1):
        self.qty += qty
        if self.qty > self.length:
            self.qty = self.length

    def getString(self):
        return "{desc}: {qty}/{length}".format(**self.__dict__)


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
            if v == cmd.split(' ')[0]:
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

    defFlags =  { "subTurn": 0
                , "turns": 0
                , "score": 0
                , "hair": 1
                , "sit": False
                }

    force = ""
    done = False

    defStrings= { 'fail': 'Hmm...'
                }

    defVerbs = ["debug", "help", "exit", "hint", "score", "save", "load", "restart"]

    fancyVerbs ={ "==>": "_mspa"
                , "saves": "showsaves"
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
        self.banned = []
        self.achievements = {}
        self.lastSave = "default"

    def __getstate__(self):
        return self.currRoom, self.inv, self.flags, self.rooms, self.items, self.lastSave, self.achievements

    def __setstate__(self, state):
        self.currRoom, self.inv, self.flags, self.rooms, self.items, self.lastSave, self.achievements = state

    def initScreens(self, Interface, Screen, Renderer):
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
        rend = Renderer(self.interface)

    def commandLoop(self, infile = None):
        """
        Runs the game.
        """
        self.interface.commandLoop(infile)

    def loadModules(self):
        """
        Loads rooms from all modules in rooms/*.py. and sets
        inventory to the room named 'inv', which must exist.
        """
        with open("logs/gameload", "w") as f:
            roomFiles = os.listdir('./rooms')
            items = []
            combos = []
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
                            elif Combo in inspect.getmro(thing):
                                try:
                                    nCombo = thing()
                                    combos.append(nCombo)
                                except Exception as e:
                                    f.write(str(e)+'\n')
 
                        except Exception as e:
                            pass

            for item in items:
                room = self.rooms[item.loc]
                room.items[item.name] = item
                item.room = room
                f.write("Adding item {} to room {}\n".format(item.name, room.name))

            for combo in combos:
                room = self.rooms[combo.loc]
                room.combos[combo.name] = combo
                combo.room = room
                f.write("Adding combo {} to room {}\n".format(combo.name, room.name))

            self.inv = self.rooms['inv']

            for name, desc, qty in achieve.achievements:
                self.achievements[name] = Achievement(desc, qty)

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
        if cmd.split(' ')[0] in self.banned:
            pass
        elif self.inv.doCmd(cmd):
            pass
        elif self.currRoom.doCmd(cmd):
            pass
        elif self._doCmd(cmd):
            pass
        else:
            say(self.getString('fail'))
        self.refreshImg()

    def giveAchievement(self, name, qty = 1):
        """
        Gives the player qty progress towards the named
        achievement.
        """
        self.achievements[name].give(qty)

    def getAchievements(self):
        """
        Formats and returns a list of strings for the
        player's achievements.
        """
        strings = [x.getString() for x in self.achievements.values()]
        result = []       

        strings = sorted(strings, key=lambda x: len(x)) 

        return strings

    def moveRoom(self, name):
        """
        Changes the current room, refreshes rendering info,
        and calls exit and enter functions.
        """
        if self.currRoom:
            self.currRoom._onLeave()
        self.banned = []
        self.currRoom = self.rooms[name]
        self.refreshImg()
        self.currRoom._onEnter()

    def banVerbs(self, verbs):
        """
        Temporarily ban the given verbs from being
        recognized. Cleared on moveRoom.
        """
        self.banned.extend(verbs)

    def moveItem(self, name, newLoc):
        """
        Move the named unique item to the given room.
        """
        self.items[name]._move(newLoc)

    def hasItem(self, name):
        """
        Checks to see if an item with the given name is in
        the inventory and returns the quantity.
        """
        if name in self.inv.items.keys():
            return self.inv.items[name].qty
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

    def _clear(self):
        """
        Clear and reload data.
        """
        self.__init__()
        self.interface.clear()
        self.loadModules()

    def restart(self, cmd):
        """
        Restart the game. Starts in the room named _init.
        """
        #TODO: Check unsaved game and confirm if so?
        self._clear()
        self.moveRoom('_init')

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
        self.refreshImg()
        say("Loaded gamed {}.".format(self.lastSave))
        return True

    def showsaves(self, cmd):
        saves = getSaveNames()
        result = []
        fmt = "{name:12}{loc:12}{score:12}{time:12}"
        result.append(fmt.format( name="name"
                                , loc ="room"
                                , score = "score"
                                , time = "turns"
                                ))
        for name in saves:
            loadGame = load(self, name)
            if loadGame != None:
                result.append(fmt.format( name=name
                                        , loc=loadGame.currRoom.name
                                        , score=str(loadGame.getScore())
                                        , time=str(loadGame.getTurns())
                                        ))
        
        game.say('\n'.join(result))
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
    items. The current room catches
    commands from the player and handles them or passes
    them to items that can. The inventory is a special room
    that also catches commands and holds items in the
    player's inventory.

    Rooms can be entered and exited and will call the
    functions _onFirstEnter, _onOtherEnter, and _onLeave.

    Rooms presently have some shoddy sit/stand functionality.
    Items live in a dictionary as items[name].
    """
    name = ""
    sitable = False         #Can the player sit?

    defVerbs = ["look", "sit", "stand"]

    defStrings= { "desc": "It is a room?"
                , "closer": "You take a closer look."
                , "loc": "You are {pos}."
                , "sit": "There's nowhere to sit!"
                , "sit2": "You are already sitting."
                , "stand": "You stand up. You are now standing."
                , "stand2": "You are already standing."
                , "sitFail": "You can't do that while sitting?"
                }

    defFlags = {}
    flagDec = '~'

    def __init__(self):
        Bld.__init__(self)

        self.items = {}
        self.combos = {}
        self.defFlags['entered'] = False

    def _show(self):
        rend.clear()
        Bld._show(self)
        for item in self.items.values():
            item._show()

    def _hide(self):
        rend.clear()

    def _makeItemString(self, obscure = False):
        """
        Formats a description of items in the room, exluding
        obscure items.
        """
        itemStrings = []
        for item in self.items.values():
            if item.obscure == obscure:
                itemStrings.append( item.getGround() )
        return ' '.join(itemStrings)

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
        for item in self.items.values():
            verbs.extend(item.getVerbs())
        return verbs

    def doCmd(self, cmd):
        """
        Checks commands on items first, then on self.
        """
        for combo in self.combos.values():
            if combo._checkCmd(cmd):
                if combo._doCmd(cmd):
                    return True 
        for item in self.items.values():
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

    def sit(self, cmd):
        """
        Handles sitting in various directions. Is stupid and
        should be reworked.
        """
        state = g.getFlag("sit")

        if state:
            return fail(self.getString("sit2"))

        return self.sitDown()

    def stand(self, cmd):
        """
        Same dead as sit. Blam this piece of crap.
        """
        state = g.getFlag("sit")

        if not state:
            return fail(self.getString("stand2"))

        return self.standUp()

    def sitDown(self):
        if self.sitable:
            g.setFlag('sit', True)
            say(self.getString("sit"))
            return True
        return fail(self.getString("sit"))

    def standUp(self):
        say(self.getString("stand"))
        g.setFlag('sit', False)
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
    defVerbs = ["look", "take", "drop"]
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
    flagDec = '`'
    defLoc = ""
    defQty = 1
    defSprite = None

    def  __init__(self):
        if self.useable:
            self.addVerbs.append("use")
        Bld.__init__(self)
        self.qty = self.defQty
        self.loc = self.defLoc

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

    def _move(self, newLoc):
        """
        Move the item to a different room and position. If
        no position is given, uses the player's last known
        location in the room. Also handles quantities and
        Item duplication/removal for non-unique items.
        """
        oldRoom = self.room

        if self.unique or self.qty == 1:
            del oldRoom.items[self.name] 
        else:
            self.qty -=1

        nRoom = g.rooms[newLoc]

        if self.unique:
            nRoom.items[self.name] = self
            self.room = nRoom
            self.loc = newLoc
        else:
            if self.name in nRoom.items.keys():
                nRoom.items[self.name].qty += 1
            else:
                nItem = self.__class__()
                nItem.qty = 1
                nItem.loc = newLoc
                nItem.room = nRoom
                nRoom.items[self.name] = nItem 

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

    def take(self, cmd):
        """
        Takes the item if takeable. If the item is unique
        and in the player's inventory, says the have
        descriptive string. If the item is not unique,
        passes so that identical items in the room can catch
        the command.
        If the take succeeds, prints the take descriptive
        string.
        """
        if self.takeable == False:
            if 'take' in self.strings.keys():
                return fail(self.getString('take'))
            return fail()
        if self.loc == 'inv':
            if not self.unique:
                return _pass()
            return fail(self.getString("have"))

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
        player's current room.
        """
        if self.loc != 'inv':
            return _pass()
        if self.hidden:
            return fail()
        say(self.getString('drop'))
        if self.dropable:
            room = g.currRoom
            self._move(room.name)
            return True
        return False


class Combo(Bld):
    """
    For handling commands containing pairs of items with a
    conjunction. Commands caught have the form
    VERB LEFT CONJUCTION RIGHT.
    Combos are checked before items.
    """

    name = "combo"

    directional = False     #whether left/right order matters

    strings =   {
                }
    
    defFlags =  {
                }
    flagDec = '+'

    room = None
    defLoc = ""

    left = 'left'
    right = 'right'
    
    conj =  {
            }

    def  __init__(self):
        Bld.__init__(self)
        self.loc = self.defLoc
        self.left = self.left
        self.right = self.right

    def _checkConj(self, cmd, conj, left, right):
        if len(cmd) < len(left) + len(right) + 3:
            return False

        if cmd[:len(left)] != left or cmd[len(left)] != ' ':
            return False 
        
        cmd = cmd[len(left)+1:]
        c = cmd.split(' ')[0]
        if not c in conj:
            return False

        if right != ' '.join(cmd.split(' ')[1:]):
            return False
        return True


    def _checkCmd(self, cmd):
        parts = cmd.split(' ')
        rest = ' '.join(cmd.split(' ')[1:])
        verb = parts[0]

        if not verb in self.verbs.keys():
            return False
        conj = self.conj[verb]

        if self._checkConj(rest, conj, self.left, self.right):
            return True
        if not self.directional and self._checkConj(rest, conj, self.right, self.left):
            return True
        return False


    def _doCmd(self, cmd):
        if not self._checkCmd(cmd):
            return _pass()

        return Bld._doCmd(self, cmd)

    def voidVerb(self, verb):
        if verb in self.verbs.keys():
            del self.verbs[verb]







