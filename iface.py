import game
import os, sys, time, re
import readline
import pdb
import curses
from curses.textpad import Textbox

class Screen():
    width = 60
    height = 45
    cmdHeight = 23
    txtWidth = 60

    def __init__(self):
        self.buffer=['']

    def checkWord(self, word):
        length = len(self.buffer[-1])
        if length == 0:
            return False
        if length + len(word) > self.txtWidth -1:
            return True
        else:
            return False

    def sayBit(self, data):
        self.buffer[-1] += data
        sys.stdout.write(data.upper())
        sys.stdout.flush()

    def lf(self):
        self.sayBit('\n')
        self.buffer.append('')
        self.line = ''

    def sayWord(self, word):
        if self.checkWord(word):
            self.lf()
        if len(self.buffer[-1]) > 0:
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


class CurseScreen(Screen):

    height = 24
    cmdHeight = 9
    txtWidth = 59
    width = 60

    def __init__(self):
        self.buffer=[' ']
        self.offset = 0

    def setWindow(self, win):
        self.window = win

    def sayBit(self, data):
        self.buffer[-1] += data
        self.paint()

    def lf(self):
        self.buffer.append('')

    def drawScrollBar(self):
        self.window.vline(0, self.width-1, curses.ACS_VLINE, self.cmdHeight)
        if len(self.buffer) > self.cmdHeight:
            pos = int((self.cmdHeight-1) * (1 - float(self.offset)/(len(self.buffer)-self.cmdHeight)))
            char = curses.ACS_TTEE if pos == 0 else curses.ACS_BTEE if pos == self.cmdHeight -1 else curses.ACS_PLUS
            self.window.addch(pos, self.width-1, char)

    def paint(self):
        i = 0
        length = len(self.buffer) - self.offset
        for i, line in enumerate(self.buffer[length-self.cmdHeight:length]):
            self.window.addstr(i, 0, line.upper())
            for match in re.finditer("green", line): 
                self.window.addstr(i, match.start(), "GREEN", curses.color_pair(1))
 
        self.drawScrollBar()
        self.window.refresh() 
        self.window.clear()           

    def home(self):
        self.offset = 0
        self.paint()

    def page(self, amt):
        self.offset += amt
        if self.offset < 0:
             self.offset = 0
        if self.offset > len(self.buffer)-self.cmdHeight:
            self.offset = len(self.buffer)-self.cmdHeight
        self.paint() 

    def pageUp(self):
        self.page(-1)

    def pageDown(self):
        self.page(1)



class CurseInterface():

    cmdwin = None

    def __init__(self,g):
        self.g = g 
        self.infile = sys.stdin
        self.stdscr = curses.initscr()
        self.history = []

    def setScreen(self, scr):
        self.scr = scr
        self.imgwin = curses.newwin(self.scr.height-self.scr.cmdHeight-1, self.scr.width, 0,0)
        self.cmdwin = curses.newwin(self.scr.cmdHeight+1, self.scr.width, self.scr.height-self.scr.cmdHeight-1, 0) 
        self.inwin = curses.newwin(1, self.scr.width, self.scr.height-1, 0)
        self.cmdwin.leaveok(1)
        self.tbox = Textbox(self.inwin)

        self.imgwin.border()
        self.imgwin.refresh()

        curses.start_color()
s       curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)

    def refreshCmd(self, cmd):
        self.inwin.clear() 
        self.inwin.addstr(0,0, "> "+cmd.upper())
        return len(cmd)

    def getCmd(self, f):
        
        self.scr.paint()
        curses.noecho()
        cmd = ""
        force = not self.g.force == ""
        if force:
            forceCmd = self.g.force
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
            elif char == curses.KEY_NPAGE:
                self.scr.pageUp()
            elif char == curses.KEY_PPAGE:
                self.scr.pageDown()
            else:
                self.scr.home()
                if not force:
                    cmd += chr(char)
                elif xpos < len(forceCmd):
                    cmd += forceCmd[xpos]
                xpos += 1
                if force and xpos >= len(cmd):
                    xpos = len(cmd)-1
                cmdTemp = cmd
            xpos = self.refreshCmd(cmd)
            self.inwin.refresh()

        if force:
            cmd = forceCmd

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
            game.say("> "+cmd)

            self.g.doCmd(cmd)

            self.scr.paint()

        curses.endwin()




