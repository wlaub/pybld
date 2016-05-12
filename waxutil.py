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
        self.selectmode = None

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
        elif char == curses.KEY_SRIGHT:
            self.x = self.w-1
        elif char == curses.KEY_SLEFT:
            self.x = 0
        elif char == curses.KEY_SF:
            self.y = self.h-1
        elif char == curses.KEY_SR:
            self.y = 0
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

    def _selectRange(self):
        left = min(self.x, self.sx)
        right = max(self.x, self.sx)
        top = min(self.y, self.sy)
        bottom = max(self.y, self.sy)
        return left, right, top, bottom

    def select(self, cmd, image, color):
        self.win.move(self.y, self.x)
        self._startSelect()
        l, r, t, b = self._selectRange()
        if self.handleCursors(cmd):
            return True
        elif cmd == ord('f'):
            for x in range(l, r+1):
                for y in range(t, b+1):
                    self.win.addch(y, x, curses.ACS_BULLET, curses.color_pair(color))
            self.win.refresh()  
            fill = self.win.getch()
            char = self.cmdToChar(fill)
            if char != None:
                for x in range(l, r+1):
                    for y in range(t, b+1):
                        image.write(y, x, char, color)
            else:
                return True
        elif cmd == ord('c'):
            image.resize(l, r+1, t, b+1)
            return False
        self._stopSelect()
        return False


    def drawSelect(self):
        if self.selectmode:
            l, r, t, b = self._selectRange()
            curses.textpad.rectangle(self.win, t, l, b, r)

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

