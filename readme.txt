#
#
#
# fancy ascii art 'pybld' goes here
#
#
#

Setup:

In your main function, create an instance of game.Game
Call game.loadModules() to load your content from ./rooms/
Set up your screens using game.initScreens(Interface,Screen)
    iface.py contains some basic screens. The default curses
    interface is CurseInterface and CursesScreen. Be sure to
    call curses.initscr() before game.initScreens()
Call game.moveRoom('name') with your first room
Class game.commandLoop() to run the game                                              
              
Game Structure:

    Bld:
        
        The base class for anything using verbs, graphics,
        and descriptive strings.

        A verb is a keyword from the player that causes a 
        function to be called e.g. "use", "look", "save".

        Plain verbs correspond to a function of identical
        name: "use" calls the function use().
        defVerbs contains the default verbs for a class,
        addVerbs contains additional verbs for a derived
        class, and rmVerbs contains verbs that should be
        exluded in a derived class.

        Fancy verbs are commands that don't match function
        names and are used to allow for verbs that contain
        weird characters. fancyVerbs is a dictionary of
        fancy verbs of the form {'verb name':'func name'}

        Verb functions are of the form
            def name(self, cmd)
        where cmd is the full command entered by the player.

        Graphics are defined by sprites from bldgfx. The
        sprite for an object is defined by defSprite e.g.
        defSprite = bldgfx.Sprite('file', ypos, xpos)
        and can be accessed within the object as self.sprite

        Descriptive strings are a dictonary of strings with
        some formatting. self.getString('name') formats and
        returns the corresponding descriptive string.
        Different derived objects may require some base
        strings, and provide different formatting options.
        "{}" is always replaced with the object name.


    Game:

        The base game class. Handles loading, setting up
        graphics, and global commands like "save", "load",
        "score", "exit" etc. You'll have to edit this class
        if you want to add additional global verbs.

        The game class also contains all the flags for the
        game, which are generally accessed using getFlag
        and setFlag functions.

        To reference the game instance, use game.g

        String options:
           TODO 

    Room:

        A room represents a distinct location in the game.
        
        A room contains sublocations (left, right, top, etc)
        and items as well as some base functionality for
        looking around and moving as well as special
        functions to be called when the player enters and
        leaves.

        To make a room, create a child class with [probably a tool]
        
        Required strings are:
            "desc": The base description of the room given
                by the 'look' command
            "closer": The description given by the 'look
                closer' command
            
        Optional strings are:
            "enter [loc]": A custom string to be displayed
                when the player moves to [loc] in the room

            "loc": A string giving the player's location in
                the room.

        String formatting names:
            'loc': The player's location in the room.




