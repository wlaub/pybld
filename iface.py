import game
import os, sys, time, re
import readline
import pdb
import curses.ascii as crsascii
import unicurses as curses
#from curses.textpad import Textbox

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

    def lf(self, num = 1):
        for i in range(num):
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
        self.buffer=['']
        self.offset = 0

    def setWindow(self, win):
        self.window = win

    def sayBit(self, data):
        self.buffer[-1] += data
        self.paint()

    def lf(self, num=1):
        for i in range(num):
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
        top = length-min(len(self.buffer), self.cmdHeight)
        bottom = length
        for i, line in enumerate(self.buffer[top:bottom]):
            self.window.addstr(i, 0,line.upper())
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
        if self.offset > len(self.buffer)-self.cmdHeight:
            self.offset = len(self.buffer)-self.cmdHeight
        if self.offset < 0:
             self.offset = 0
        self.paint() 

    def pageUp(self):
        self.page(-1)

    def pageDown(self):
        self.page(1)



class CurseInterface():

    cmdwin = None

    def __init__(self, g):
        self.g = g
        self.infile = sys.stdin
        self.stdscr = curses.initscr()
        self.history = []

    def setGame(g):
        self.g = g

    def setScreen(self, scr):
        self.scr = scr
        self.imgwin = curses.newwin(self.scr.height-self.scr.cmdHeight-1, self.scr.width, 0,0)

        self.cmdwin = curses.newwin(self.scr.cmdHeight+1, self.scr.width, self.scr.height-self.scr.cmdHeight-1, 0) 
        self.inwin = curses.newwin(1, self.scr.width, self.scr.height-1, 0)
        self.cmdwin.leaveok(1)

        self.inwin.keypad(1)
        self.inwin.leaveok(1)

        self.imgwin.leaveok(1)

        self.imgwin.border()
        self.imgwin.refresh()

        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)

    def getImgWin(self):
        return self.imgwin

    def refreshCmd(self, cmd):
        self.inwin.clear() 
        self.inwin.addstr(0,0, self.prefix+cmd.upper())
        return len(cmd)

    def getNext(self):
        if self.infile != None:
            char = self.infile.read(1)
            if char == '':
                self.infile = None
            else:
                char = ord(char)
        if self.infile == None:    
            char =self.inwin.getch()
        return char

    def validateCmd(self, val):
        force = self.g.force
        if len(force) > 0:
            if self.xpos < len(force) :
                if curses.ascii.isprint(val):
                    val = force[self.xpos].upper()
                    self.xpos +=1
                    return val
                else:
                    return 0
            else:
                return val if val == 0x0a else 0
        if val == curses.KEY_UP:
            if self.hpos > -len(self.history):
                self.hpos -= 1
                self.refreshCmd(self.history[self.hpos])
        elif val == curses.KEY_DOWN:
            if self.hpos < -1:
                self.hpos += 1 
                self.refreshCmd(self.history[self.hpos])
            elif self.hpos == -1:
                self.hpos = 0
                self.inwin.clear()
                self.inwin.addstr(0,0,"> ")
        elif val == curses.KEY_NPAGE:
            self.scr.pageUp()
        elif val == curses.KEY_PPAGE:
            self.scr.pageDown()
        if curses.ascii.isprint(val):
            val = ord(chr(val).upper())
        return val

    def getCmd(self, f, prefix = "> ", history = True):
        
        self.scr.paint()
        curses.noecho()
        cmd = ""
        force = not self.g.force == ""
        if force:
            forceCmd = self.g.force

        self.prefix = prefix

        self.inwin.clear()
        self.inwin.addstr(0,0, self.prefix)
        self.inwin.refresh()

        ###
        """
        self.xpos = 0
        self.hpos = 0
        tbox = Textbox(self.inwin.derwin(0,2))
        #game.rend.play(False)
        tbox.stripspaces = 0
        cmd = tbox.edit(self.validateCmd)[:].strip().lower()
        """
        ### 
        curses.flushinp() 
        self.xpos = 0
        hpos = 0
        cmdTemp = ''
        while 1:
            char = self.getNext()
            if char == 0x0a:
                break
            elif char == -1:
                pass
            elif char == 127 or char == curses.KEY_BACKSPACE:
                if self.xpos > 0 and not force:
                    cmd = cmd[:-1]
            elif char == 21:
                if not force:
                    cmd = ''
            elif char == curses.KEY_UP and history:
                if hpos > -len(self.history):
                    hpos -= 1
                    cmd = self.history[hpos]
            elif char == curses.KEY_DOWN and history:
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
            elif crsascii.isprint(char):
                self.scr.home()
                if not force:
                    cmd += chr(char)
                elif self.xpos < len(forceCmd):
                    cmd += forceCmd[self.xpos]
                self.xpos += 1
                if force and self.xpos >= len(cmd):
                    self.xpos = len(cmd)-1
                cmdTemp = cmd
            self.xpos = self.refreshCmd(cmd)
            self.inwin.refresh()
       
        ###
        
        if force:
            cmd = forceCmd

        self.inwin.clear()
        self.inwin.refresh()

        self.g.force = ""

        if history:
            self.history.append(cmd)

        return cmd


    def getConfirm(self, text = "Are you sure? y/n "):
        result = ''
        while result != 'y' and result != 'n':
            result = self.getCmd(self.infile, text.upper(), history=False)
        if 'y' in result:
            return True
        return False

    def getPause(self, text = "(continue)"):
        self.inwin.clear()
        self.inwin.addstr(0,0, text.upper())
        self.inwin.refresh()
       
        self.getNext()
        self.inwin.clear()
        self.inwin.refresh()


    def commandLoop(self, infile = None):
        self.infile = infile
        while not self.g.done:
            cmd = self.getCmd(self.infile)

            game.lf()
            game.say("> "+cmd)

            self.g.doCmd(cmd)

            self.scr.paint()

        curses.endwin()




