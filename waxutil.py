import time
import curses
import curses.textpad
import pdb
import image


class EditWindow():

    cchar = 1
    copyFrame = None
    copyW = 0
    copyH = 0
    x = 0
    y = 0

    def reset(self, window):
        self.win = window
        self.win.keypad(1)
        self.win.leaveok(1)
        self.h, self.w = self.win.getmaxyx()
        self.sx = 0
        self.sy = 0
        self.selectmode = None

    def __init__(self, window):
        self.reset(window)

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
        elif char == 0x20D: #ctrl+down
            self.moveCursor(3,0)
        elif char == 0x236: #ctrl+up
            self.moveCursor(-3,0)
        elif char == 0x221: #ctrl+left
            self.moveCursor(0,-5)
        elif char == 0x230: #ctrl+right
            self.moveCursor(0,5)
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
        elif cmd >= curses.KEY_F6 and cmd <= curses.KEY_F8:
            return cmd -curses.KEY_F5
        elif cmd == curses.KEY_F5:
            return ord(' ')
        elif cmd == curses.KEY_BACKSPACE:
            return 0
        return None
 
    def pickChar(self):
        cmd = self.win.getch()
        char = self.cmdToChar(cmd)
        if char != None:
            self.cchar = char

    def getChar(self):
        return self.cchar

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

    def bucket(self, image, color):
        image.bucket(self.y, self.x, self.getChar(), color) 
 
    def paste(self, image):
        if self.copyFrame != None:
            image.paste(self.y, self.x, self.copyFrame, self.copyH, self.copyW)

    def select(self, cmd, image, color):
        self.win.move(self.y, self.x)
        self._startSelect()
        l, r, t, b = self._selectRange()
        if self.handleCursors(cmd):
            return True
        elif cmd == ord('f'):
           for x in range(l, r+1):
                for y in range(t, b+1):
                    image.write(y, x, self.cchar, color)
        elif cmd == ord('c'):
            image.resize(l, r+1, t, b+1)
            return False
        elif cmd == ord('y'):
            self.copyFrame, self.copyH, self.copyW = image.copyArea(l, r+1, t, b+1)
        self._stopSelect()
        return False


    def drawSelect(self):
        if self.selectmode:
            l, r, t, b = self._selectRange()
            curses.textpad.rectangle(self.win, t, l, b, r)

    def drawCopy(self):
        if self.copyFrame != None:
            self.copyFrame.draw(self.win, self.y, self.x)

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

