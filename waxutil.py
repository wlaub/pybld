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
        if self.x >= self.w:
            self.x = self.w-1
        if self.y >= self.h:
            self.y = self.h-1
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

    def bucket(self, hist, color):
        hist.change('bucket', self.y, self.x, self.getChar(), color)
 
    def paste(self, hist):
        if self.copyFrame != None:
            hist.change('paste', self.y, self.x, self.copyFrame, self.copyH, self.copyW)

    def select(self, cmd, name, hist, color):
        image = hist.getImage()
        self.win.move(self.y, self.x)
        self._startSelect()
        l, r, t, b = self._selectRange()
        if self.handleCursors(cmd):
            return True
        elif name == 'fill':
            hist.change('fillArea', l, r+1, t, b+1, self.cchar, color)
        elif name == 'crop':
            hist.change('resize', l, r+1, t, b+1)
            return False
        elif name == 'copy':
            self.copyFrame, self.copyH, self.copyW = image.copyArea(l, r+1, t, b+1)
        elif name == 'delete':
            hist.change('fillArea', l, r+1, t, b+1, 0, color)
        elif name == 'cut':
            self.copyFrame, self.copyH, self.copyW = image.copyArea(l, r+1, t, b+1)
            hist.change('fillArea', l, r+1, t, b+1, 0, color)
        self._stopSelect()
        return False


    def drawSelect(self):
        if self.selectmode:
            l, r, t, b = self._selectRange()
            try:
                self.win.leaveok(1)

                if r>l:
                    self.win.hline(t, l+1, curses.ACS_HLINE, r - l - 1)
                    self.win.hline(b, l+1, curses.ACS_HLINE, r - l - 1)
                if b > t:
                    self.win.vline(t+1, l, curses.ACS_VLINE, b - t - 1)
                    self.win.vline(t+1, r, curses.ACS_VLINE, b - t - 1)
                self.win.addch(t, l, curses.ACS_PLUS)
                self.win.addch(t, r, curses.ACS_PLUS)

                self.win.addch(b, l, curses.ACS_PLUS)
                self.win.addch(b, r, curses.ACS_PLUS)
            except:
                pass

    def drawCopy(self):
        if self.copyFrame != None:
            self.copyFrame.draw(self.win, self.y, self.x)

    def edit(self, hist, color):
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
            hist.partChange('write', self.y, self.x, char, color) 
            self.moveCursor(0,1)
        elif cmd == 0x1b:
            hist.endEdit()
            return False
        return True

class Validator():
    def __init__(self):
        self.abort = False 

    def validate(self, val):
        if val == 0x1b:
            self.abort = True
            return 0x07
        return val


class CommandMap():

    def __init__(self):
        self.charMap =  { curses.KEY_LEFT: curses.ACS_LARROW
                        , curses.KEY_RIGHT: curses.ACS_RARROW
                        , curses.KEY_UP: curses.ACS_UARROW
                        , curses.KEY_DOWN: curses.ACS_DARROW
                        , curses.KEY_SLEFT: curses.ACS_LARROW
                        , curses.KEY_SRIGHT: curses.ACS_RARROW
                        , curses.KEY_SR: curses.ACS_UARROW
                        , curses.KEY_SF: curses.ACS_DARROW

                        }
        self.charMap[ord('\t')] =  unichr(0x21A6).encode(image.code)


    def parseCommandData(self,cmd, data):
        name = data[0]
        if cmd in self.charMap.keys():
            char = self.charMap[cmd]
        else:
            char = chr(cmd)
        if len(data) > 1:
            desc = data[1]
        else:
            desc = name
        return name, char, desc


    def parseCommand(self, cmd):
        if cmd in self.commands.keys():
            data = self.commands[cmd]
            return self.parseCommandData(cmd, data)
        return None, None, None

    def parseCommandName(self, name):
        for key, data in self.commands.iteritems():
            if data[0] == name:
                return self.parseCommandData(key, data)
        return None, None, None

    def draw(self, window):
        hspace = 15 
        for i, block in enumerate(self.blocks):
            for y, n in enumerate(block):
                n, sym, desc = self.parseCommandName(n)
                try:
                    window.addch(y, i*hspace, sym, curses.color_pair(4))
                except:
                    window.addstr(y, i*hspace, sym, curses.color_pair(4))
                try:
                    window.addstr(y, i*hspace+2, desc)
                except:
                    pass
       
class DefMap(CommandMap): 
    def __init__(self):
        CommandMap.__init__(self)
        self.blocks = [ ['new', 'save', 'load', 'open', 'close', 'quit']
                        , ['edit', 'select', 'paste', 'char', 'color', 'bucket', 'resize']
                        , ['frame', 'frame length', 'next frame', 'prev frame']
                        , ['play', 'alpha', 'cursor', 'scopy', 'prev img', 'next img']
                        ]
        self.commands = { ord('n'): ['new']
                        , ord('s'): ['save']
                        , ord('l'): ['load']
                        , ord('o'): ['open']
                        , ord('c'): ['close']
                        , ord('q'): ['quit']
                        
                        , ord('i'): ['edit']
                        , ord('v'): ['select']
                        , ord('f'): ['frame', 'new frame']
                        , ord('r'): ['resize']
                        , ord('\\'): ['char', 'set char']
                        , ord('d'): ['paste']
                        , ord('b'): ['bucket', 'bucket fill']
                        , ord('g'): ['color', 'toggle color']
                        
                        , ord('a'): ['alpha', 'show alpha']
                        , ord('p'): ['play', 'play/pause']
                        , curses.KEY_RIGHT: ['next frame']
                        , curses.KEY_LEFT: ['prev frame']
                        , ord('?'): ['frame length']
                        , ord('\t'): ['cursor', 'show cursor']
                        , ord('1'): ['scopy', 'show copy' ]
                        
                        , curses.KEY_UP: ['prev img']
                        , curses.KEY_DOWN: ['next img']
                        , curses.KEY_SR: ['up']
                        , curses.KEY_SF: ['down']
                        , curses.KEY_SLEFT: ['left']
                        , curses.KEY_SRIGHT: ['right']
                        }

class SymMap(CommandMap):
    def __init__(self):
        CommandMap.__init__(self)
        self.blocks = [ ['new', 'save', 'load', 'open', 'close', 'undo', 'redo']
                        , ['edit', 'select', 'paste', 'char', 'color', 'bucket', 'resize']
                        , ['frame', 'del frame', 'frame length', 'next frame', 'prev frame']
                        , ['play', 'alpha', 'cursor', 'scopy', 'prev img', 'next img']
                        ]
        self.commands = { ord('w'): ['new']
                        , ord('s'): ['save']
                        , ord('d'): ['load']
                        , ord('e'): ['open']
                        , ord('c'): ['close']
                        , ord('q'): ['quit']
                        
                        , ord('t'): ['edit']
                        , ord('v'): ['select']
                        , ord('n'): ['frame', 'new frame']
                        , ord('j'): ['del frame']
                        , ord('r'): ['resize']
                        , ord('y'): ['char', 'set char']
                        , ord('b'): ['paste']
                        , ord('f'): ['bucket', 'bucket fill']
                        , ord('g'): ['color', 'toggle color']
                        
                        , ord('i'): ['alpha', 'show alpha']
                        , ord('p'): ['play', 'play/pause']
                        , curses.KEY_RIGHT: ['next frame']
                        , curses.KEY_LEFT: ['prev frame']
                        , ord('h'): ['frame length']
                        , ord('k'): ['cursor', 'show cursor']
                        , ord('o'): ['scopy', 'show copy' ]
                        , ord('z'): ['undo'] 
                        , ord('x'): ['redo']

                        , curses.KEY_UP: ['prev img']
                        , curses.KEY_DOWN: ['next img']
                        , curses.KEY_SR: ['up']
                        , curses.KEY_SF: ['down']
                        , curses.KEY_SLEFT: ['left']
                        , curses.KEY_SRIGHT: ['right']

                        , ord('~'): ['debug']
                        }



class SelMap(CommandMap):
   
    def __init__(self):
        CommandMap.__init__(self)
        self.blocks = [['crop', 'fill', 'copy', 'delete', 'cut']]
        self.commands =   { ord('c'): ['crop']
                            , ord('f'): ['fill']
                            , ord('y'): ['copy']
                            , ord('d'): ['delete']
                            , ord('x'): ['cut']
                            }

        
