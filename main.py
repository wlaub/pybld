#!/usr/bin/python
import time, sys, os
import rooms, game, iface, bldgfx
import readline
import curses
import pdb


if __name__ == "__main__":
    infile = sys.stdin
    if len(sys.argv) > 1:
        infile = open(sys.argv[1], 'r')

    g = game.Game()
    g.loadModules()

    try:
        mainScreen = curses.initscr()

        curses.resizeterm(45, 60)

        g.initScreens(iface.CurseInterface, iface.CurseScreen, bldgfx.Renderer)
        g.moveRoom('First Room')
        g.commandLoop(infile)
    except Exception as e:
        curses.endwin()
        pdb.set_trace()
        raise


