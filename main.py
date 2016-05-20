import time, sys, os
import rooms, game, iface, bldgfx
import readline
import curses

g = game.Game()

g.loadModules()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        infile = open(sys.argv[1], 'r')

    try:
        interface = iface.CurseInterface(g)
        screen = iface.CurseScreen()
        interface.setScreen(screen)
        screen.setWindow(interface.cmdwin)

        rend = bldgfx.Renderer(interface.imgwin)

        game.rend = rend

        testbg = bldgfx.Sprite('img/sunset.bmi',0,0, -1)
        testSprite = bldgfx.Sprite('img/flashy.bmi', 0, 0, 1)
        sprite2 = bldgfx.Sprite('img/flashy.bmi', 2, 2, 1)
        rend.addSprite(testSprite)
        rend.addSprite(testbg)
        rend.addSprite(sprite2)

        game.scr = screen
        g.refreshImg()
        

        interface.commandLoop()
    except:
        curses.endwin()
        raise


