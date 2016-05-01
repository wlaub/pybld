import time, sys, os
import rooms, game
import readline

g = game.Game()

g.loadModules()

currRoom = g.rooms['First Room']
inv = g.rooms['inv']
file = sys.stdin

def getCmd(f):
    cmd = raw_input("> ").lower().strip()
#    cmd = f.readline().lower().strip()

    if g.force != "":
        cmd = g.force
        g.force = ""

    return cmd

def _getCmd(f):
    read = ""
    temp = f.read(1)
    f.flush()
    force = g.force != ""
    while temp != '\n':
        read += g.force[len(read)] if force else temp
        temp = f.read(1)
        f.flush()
        sys.stdout.write('\r'+read.upper())
        sys.stdout.flush()

    return read

def replaceHistory(string):
    i = readline.get_current_history_length()
    readline.replace_history_item(i-1, string)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        file = open(sys.argv[1], 'r')

    while not g.done:

        cmd = getCmd(file)

        if cmd == '':
            file = sys.stdin
            cmd = sys.stdin.readline().lower().strip()

        replaceHistory(cmd.upper())

        if os.name == 'posix':
            sys.stdout.write("\033[1A\r")
            sys.stdout.flush()
        print("> "+cmd.upper())
        g.doCmd(cmd)


