import time, sys, os
import rooms, game, iface
import readline

g = game.Game()

g.loadModules()

currRoom = g.rooms['First Room']
inv = g.rooms['inv']
file = sys.stdin

ac = iface.AutoCompleter(g)
readline.set_completer(ac.complete)
readline.set_completion_display_matches_hook(ac.showMatches)
readline.parse_and_bind('tab: complete')

def getCmd(f):
    cmd = raw_input("> ").lower().strip()

    if g.force != "":
        cmd = g.force
        g.force = ""

    return cmd


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


