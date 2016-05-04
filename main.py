import time, sys, os
import rooms, game, iface
import readline
import curses

g = game.Game()

g.loadModules()

currRoom = g.rooms['First Room']
inv = g.rooms['inv']

if __name__ == "__main__":
    if len(sys.argv) > 1:
        infile = open(sys.argv[1], 'r')

#    interface = iface.Interface(g)
    try:
        interface = iface.CurseInterface(g)
        screen = iface.CurseScreen()
        interface.setScreen(screen)
        screen.setWindow(interface.cmdwin)
        game.scr = screen

        interface.commandLoop()
    except:
        curses.endwin()
        raise


