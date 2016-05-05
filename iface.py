import game
import os, sys, time
import readline
import pdb
import curses
from curses.textpad import Textbox

class Screen():
    width = 60
    height = 45

    def __init__(self):
        self.buffer=[]
        self.line = ""

    def checkWord(self, word):
        if len(self.line) == 0:
            return False
        if len(self.line) + len(word) > self.width -1:
            return True
        else:
            return False

    def sayBit(self, data):
        self.line += data
        sys.stdout.write(data.upper())
        sys.stdout.flush()

    def lf(self):
        self.buffer.append(self.line)
        self.sayBit('\n')
        self.line = ''

    def sayWord(self, word):
        if self.checkWord(word):
            self.lf()
        if len(self.line) > 0:
            self.sayBit(' ') 
        self.sayBit(word)

    def spell(self, data, delay=.75):
        
        if self.checkWord(data):
            self.lf()
        
        for c in data:
            self.sayBit(c)
            time.sleep(delay)

    def sayLine(self, data):
        for word in data.split(' '):
            self.sayWord(word)

    def say(self, data):
        if data.strip() != "" and data != None:
            for line in data.split('\n'):
                self.sayLine(line)
                self.lf()


class CurseScreen(Screen):

    def __init__(self):
        self.buffer=[' ']*24
        self.line = ""

    def setWindow(self, win):
        self.window = win

    def sayBit(self, data):
        self.line += data
        self.paint()

    def lf(self):
        self.buffer.append(self.line)
        self.line = ''

    def paint(self):
        i = 0
        for i, line in enumerate(self.buffer[-22:]):
            self.window.addstr(i, 0, line.upper())
        try:
            self.window.addstr(i+1, 0, self.line.upper())
        except:
            pdb.set_trace()
            raise
        

        self.window.refresh() 
        self.window.clear()           
 


class AutoCompleter():

    def __init__(self, g):
        self.g = g

    def complete(self, text, state):
        verbs = list(set(self.g.getVerbs()))
        count = 0
        matches = [v for v in verbs if v.startswith(text)]
        for v in verbs:
            if v.startswith(text):
                if count == state:
                    return v
                count+=1

        return None

    def showMatches(self, sub, matches, longest):
        return ""


class Interface():


    def __init__(self, g):
        self.g = g
        self.ac = AutoCompleter(self.g)
        readline.set_completer(self.ac.complete)
        readline.set_completion_display_matches_hook(self.ac.showMatches)
        readline.parse_and_bind('tab: complete')

        self.infile = sys.stdin

    def getCmd(self, f):
        cmd = raw_input("> ").lower().strip()

        if self.g.force != "":
            cmd = self.g.force
            self.g.force = ""

        return cmd


    def replaceHistory(self, string):
        i = readline.get_current_history_length()
        readline.replace_history_item(i-1, string)


    def commandLoop(self):
        while not self.g.done:
            cmd = self.getCmd(self.infile)

            if cmd == '':
                self.infile = sys.stdin
                cmd = sys.stdin.readline().lower().strip()

            self.replaceHistory(cmd.upper())

            if os.name == 'posix':
                sys.stdout.write("\033[1A\r")
                sys.stdout.flush()
            print("> "+cmd.upper())
            self.g.doCmd(cmd)


class CurseInterface():

    cmdwin = None

    def __init__(self,g):
        self.g = g 
        self.infile = sys.stdin
        self.stdscr = curses.initscr()
        self.history = []

    def setScreen(self, scr):
        self.scr = scr
        self.cmdwin = curses.newwin(24, self.scr.width, 0, 0) 
        self.inwin = curses.newwin(1, self.scr.width, 23, 0)
        self.cmdwin.leaveok(1)
        self.tbox = Textbox(self.inwin)

    def refreshCmd(self, cmd):
        self.inwin.clear() 
        self.inwin.addstr(0,0, "> "+cmd.upper())
        return len(cmd)

    def getCmd(self, f):
        
        curses.noecho()
        cmd = ""
        force = not self.g.force == ""
        if force:
            cmd = self.g.force
        self.inwin.clear()
        self.inwin.addstr(0,0, "> ")
        self.inwin.refresh()

        xpos = 0
        hpos = 0
        cmdTemp = ''
        while 1:
            char =self.inwin.getch()
            if char == 0x0a:
                break
            elif char == -1:
                pass
            elif char == 127 or char == curses.KEY_BACKSPACE:
                if xpos > 0 and not force:
                    cmd = cmd[:-1]
            elif char == 21:
                if not force:
                    cmd = ''
            elif char == curses.KEY_UP:
                if hpos > -len(self.history):
                    hpos -= 1
                    cmd = self.history[hpos]
            elif char == curses.KEY_DOWN:
                if hpos < -1:
                    hpos += 1 
                    cmd = self.history[hpos]
                elif hpos == -1:
                    hpos = 0
                    cmd = cmdTemp
            else:
                if not force:
                    cmd += chr(char)
                xpos += 1
                if force and xpos >= len(cmd):
                    xpos = len(cmd)-1
                cmdTemp = cmd
            xpos = self.refreshCmd(cmd)
            self.inwin.refresh()

        self.inwin.clear()
        self.inwin.refresh()

        self.g.force = ""

        self.history.append(cmd)

        return cmd


    def commandLoop(self):
        self.infile = open(sys.argv[1],'r')
        while not self.g.done:
            cmd = self.getCmd(self.infile)

            game.lf()
            game.say("> "+cmd.upper())

            self.g.doCmd(cmd)

            self.scr.paint()

        curses.endwin()




