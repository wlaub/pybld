import time, sys
import rooms, game

g = game.Game()

g.loadModules()

currRoom = g.rooms['First Room']
inv = g.rooms['inv']


while not g.done:
    sys.stdout.write("> ")
    cmd = sys.stdin.readline().lower().strip()
    if g.force != "":
        cmd = g.force
    g.force = ""

    print("\r> "+cmd.upper())

    g.doCmd(cmd)


