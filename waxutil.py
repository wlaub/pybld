import time
import curses
import pdb
import image


class EditWindow():

    def __init__(self, window):
        self.win = window
        self.x = 0
        self.y = 0
        self.win.keypad(1)
        self.h, self.w = self.win.getmaxyx()

    def moveCursor(self, y, x):
        self.y += y
        self.x += x
        self.y = max(0, min(self.y, self.h-1))
        self.x = max(0, min(self.x, self.w-1))

    def edit(self, image, color):
        self.win.move(self.y, self.x)
        char = self.win.getch()
        if char == curses.KEY_DOWN:
            self.moveCursor(1,0)
        elif char == curses.KEY_UP:
            self.moveCursor(-1,0)
        elif char == curses.KEY_LEFT:
            self.moveCursor(0,-1)
        elif char == curses.KEY_RIGHT:
            self.moveCursor(0,1)
        elif char == curses.KEY_MOUSE:
            mouse = curses.getmouse() 
            if self.win.enclose(mouse[2], mouse[1]):
                self.y = mouse[2]-1
                self.x = mouse[1]-1
        elif curses.ascii.isprint(char):
            image.write(self.y, self.x, char, color)
            self.moveCursor(0,1)
        elif char >= curses.KEY_F2 and char <= curses.KEY_F4:
            image.write(self.y, self.x, char-curses.KEY_F1, color)
        elif char == curses.KEY_BACKSPACE:
            image.write(self.y, self.x, 0, 0)
        elif char == 0x1b:
            return False
        return True

