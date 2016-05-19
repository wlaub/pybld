import time, sys, os
import rooms, game, iface, bldgfx
import readline
import curses

g = game.Game()

g.loadModules()

currRoom = g.rooms['First Room']
inv = g.rooms['inv']

if __name__ == "__main__":
    if len(sys.argv) > 1:
        infile = open(sys.argv[1], 'r')

    try:
        interface = iface.CurseInterface(g)
        screen = iface.CurseScreen()
        interface.setScreen(screen)
        screen.setWindow(interface.cmdwin)

        rend = bldgfx.Renderer(interface.imgwin)

        testSprite = bldgfx.Sprite('img/flashy.bmi', 0, 0)
        rend.addSprite(testSprite)

        game.scr = screen

        

        interface.commandLoop()
    except:
        curses.endwin()
        raise


