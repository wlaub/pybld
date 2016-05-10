import time
import curses
import curses.textpad
import pdb
import image


class EditWindow():

    def __init__(self, window):
        self.win = window
        self.x = 0
        self.y = 0
        self.win.keypad(1)
        self.h, self.w = self.win.getmaxyx()
        self.sx = 0
        self.sy = 0
        self.selectmode = False

    def moveCursor(self, y, x):
        self.y += y
        self.x += x
        self.y = max(0, min(self.y, self.h-1))
        self.x = max(0, min(self.x, self.w-1))

    def handleCursors(self, char):
        if char == curses.KEY_DOWN:
            self.moveCursor(1,0)
        elif char == curses.KEY_UP:
            self.moveCursor(-1,0)
        elif char == curses.KEY_LEFT:
            self.moveCursor(0,-1)
        elif char == curses.KEY_RIGHT:
            self.moveCursor(0,1)
        else:
            return False
        return True

    def cmdToChar(self, cmd):
        if curses.ascii.isprint(cmd):
            return cmd
        elif cmd >= curses.KEY_F2 and cmd <= curses.KEY_F4:
            return cmd-curses.KEY_F1
        elif cmd == curses.KEY_BACKSPACE:
            return 0
        return None
 
    def _startSelect(self):
        if not self.selectmode:
            self.selectmode = True
            self.sx = self.x
            self.sy = self.y

    def _stopSelect(self):
        self.selectmode = False

    def select(self, cmd):
        self.win.move(self.y, self.x)
        self._startSelect()
        if self.handleCursors(cmd):
            return True
        elif cmd == ord('f'):
            fill = self.win.getch()
            char = self.cmdToChar(fill)
            if char != None:
                for x in range(self.sx, self.x):
                    for y in range(self.sy, self.y):
                        pass
        self._stopSelect()
        return False


    def drawSelect(self):
        if self.selectmode:
            curses.textpad.rectangle(self.win, self.sy, self.sx, self.y, self.x)

    def edit(self, image, color):
        self.win.move(self.y, self.x)
        cmd = self.win.getch()
        char = self.cmdToChar(cmd)
        if self.handleCursors(cmd):
            pass
        elif cmd == curses.KEY_MOUSE:
            mouse = curses.getmouse() 
            if self.win.enclose(mouse[2], mouse[1]):
                self.y = mouse[2]-1
                self.x = mouse[1]-1
        elif char != None:
            image.write(self.y, self.x, char, color) 
            self.moveCursor(0,1)
        elif cmd == 0x1b:
            return False
        return True

