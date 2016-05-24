import time, sys, os
import rooms, game, iface, bldgfx
import readline
import curses
import pdb

#g = game.Game()

#g.loadModules()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        infile = open(sys.argv[1], 'r')

    try:
        curses.initscr()

#        interface = iface.CurseInterface()
#        screen = iface.CurseScreen()
#        interface.setScreen(screen)
#        screen.setWindow(interface.cmdwin)
#
#        rend = bldgfx.Renderer(interface.imgwin)
#        rend.playing = False

        g = game.Game()
        g.initScreens(iface.CurseInterface, iface.CurseScreen)
        g.loadModules()

#        game.rend = rend

        game.scr = g.screen
        
        g.moveRoom('First Room')

        g.interface.commandLoop()
    except Exception as e:
        curses.endwin()
        pdb.set_trace()
        raise


