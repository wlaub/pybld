import time, sys, os, thread
import curses
from curses.textpad import Textbox
import pdb
import image, waxutil

images = []
imageIdx = 0

def addFile(filename):
    global images, imageIdx
    tImg = image.Image()
    if os.path.exists(filename):
        tImg.load(filename)
    images.append((tImg, name))


for name in sys.argv[1:]:
    addFile(name)

currName = images[imageIdx][1]
currImg = images[imageIdx][0]
editbox = None

def clamp(val, _min, _max):
    if val < _min:
        return _min
    if val > _max:
        return _max
    return val

def makeWindows(image):
    global window, cmdwin, editbox, helpwin
    window = curses.newwin(image.h+2,image.w+2,0,0)
    cmdwin = curses.newwin(2, 62, image.h+2, 0)
    helpwin = curses.newwin(7, 62, image.h+2+2, 0)

    window.keypad(1)

    if not editbox:
        editbox = waxutil.EditWindow(window.subwin(image.h, image.w, 1,1))       
    editbox.reset(window.subwin(image.h, image.w, 1,1))


def clearWindows():
    global window, cmdwin, helpwin
    window.clear()
    window.refresh()
    cmdwin.clear()
    cmdwin.refresh()
    helpwin.clear()
    helpwin.refresh()

def remakeWindows():
    global currImg
    clearWindows()
    makeWindows(currImg)

def cycleImg(val):
    global imageIdx, currName, currImg
    imageIdx += val
    if imageIdx < 0:
        imageIdx += len(images)
    if imageIdx >= len(images):
        imageIdx -= len(images)
    currName = images[imageIdx][1]
    currImg = images[imageIdx][0]
    clearWindows()
    makeWindows(currImg)

def closeImg():
    global imageIdx, currName, currImg
    del images[imageIdx]
    imageIdx = clamp(imageIdx, 0, len(images)-1)
    currName = images[imageIdx][1]
    currImage = images[imageIdx][0]
    clearWindows()
    makeWindows(currImg)

def centerWin(inwin, h, w):
    t, l = inwin.getbegyx()
    b, r = inwin.getmaxyx()
    b+= t
    r+= l
    cy = clamp((b+t)/2-h/2, t, b)
    cx = clamp((l+r)/2-w/2, l, r)
    nwin = curses.newwin(h, w, cy, cx)
    return nwin, cy, cx

def getConfirm(inwin, title, yes="yes", no="NO", default = True):
    width = max(len(title) + 2, len(yes)+len(no)+3)
    window, cy, cx = centerWin(inwin, 4, width)
    window.keypad(1)
    window.leaveok(1)
    sel = default
    while 1:
        window.clear()
        window.border()
        window.addstr(1, width/2 - len(title)/2, title)
        window.addstr(2, 1, yes, curses.A_STANDOUT if sel == True else 0)
        window.addstr(2, width-1-len(no), no, curses.A_STANDOUT if sel == False else 0)
        window.refresh()
        cmd = window.getch()
        if cmd == curses.KEY_LEFT:
            sel = True
        elif cmd == curses.KEY_RIGHT:
            sel = False
        elif cmd == 0x0a:
            break
 
    return sel


def getString(inwin, title, init = None, default = None):
    namewin, cy, cx = centerWin(inwin, 3, 25)
    namewin.border()
    namewin.addstr(0,12-len(title)/2, title)
    editwin = namewin.subwin(1,23,cy+1,cx+1) 
    if init != None:
        editwin.addstr(0,0,init)
    namewin.refresh()
    tbox = Textbox(editwin)
    result = tbox.edit().strip()
    namewin.clear()
    namewin.refresh()
    if len(result) == 0:
        return default
    return result
    


def getInt(inwin, title, init=None):
    i = None
    while i == None:
        try:
            i = int(getString(inwin, title, init, default = '-1'))
        except:
            pass
    return i
 
def getSize(inwin, initw = None, inith = None):
    w = getInt(inwin, "ENTER WIDTH", initw)
    if w == -1:
        return None, None
    h = getInt(inwin, "ENTER HEIGHT", inith)
    if h == -1:
        return None, None

    return w,h

def animate():
    global currImg, play, window
    while 1:
        time.sleep(.16)
        if play:
            window.leaveok(1)
            currImg.tick(.16)
            window.clear()
            currImg.draw(window, 1, 1)
            window.refresh()
            window.leaveok(0)

def validateName(name):
    if os.path.exists(name):
        if os.path.isdir(name):
            return False 
    return True

def curseName(val):
    for key,v in curses.__dict__.iteritems():
        if v == val:
            return key


play = False
editmode = False
selectmode = False
drawalpha =False
showcopy = False
showcursor = False

infoStrings =   [ "{name} | {w} x {h} | ({x},{y}) | {frame}/{frameCount} | {length}"
                , "{mode} mode | Color: {color} | Char: {char} | 0x{cmd:04x}"
                ]


try:
    curses.initscr()
    curses.noecho()
    curses.mousemask(1)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_RED, -1)

    makeWindows(currImg)
    listwin = curses.newwin(24, 16, 0, 62)

    cmd = 0
    color = 0
    commands = [{ 'n': 'new'
                , 's': 'save'
                , 'l': 'load'
                , 'o': 'open'
                , 'c': 'close'
                , 'q': 'quit'
                },
                { 'i': 'edit'
                , 'v': 'select'
                ,  'f': 'new frame'
                , 'r': 'resize'
                , '\\': 'set char'
                , 'd': 'paste'
                },
                { 'a': 'show alpha'
                , 'p': 'play/pause'
                , curses.ACS_LARROW: 'next frame'
                , curses.ACS_RARROW: 'prev frame'
                , '?': 'frame length'
                , 'T': 'toggle show cursor'
                , '1': 'toggle show copy' 
                }]
    selCommands =  [{ 'c': 'crop'
                    , 'f': 'fill'
                    , 'y': 'copy'
                    }]


    thread.start_new_thread(animate, ())
    while 1:

        
        info =  { 'mode': "Edit" if editmode else "select" if selectmode else "command"
                , 'color': "Green" if color else "normal"
                , 'cmd': cmd
                , 'name': currName
                , 'w': currImg.w
                , 'h': currImg.h
                , 'x': editbox.x
                , 'y': editbox.y
                , 'frame': currImg.cFrame+1
                , 'frameCount': len(currImg.frames)
                , 'length': currImg.frames[currImg.cFrame].length,
                }
        info['char'] = currImg.frames[0].transcode(editbox.getChar())

        for i, val in enumerate(infoStrings): 
            cmdwin.addstr(i,0,val.format(**info))

        window.clear()
        if drawalpha:
            for y in range(currImg.h):
                window.addstr(y+1, 1, ' '*currImg.w, curses.color_pair(3))

        window.border()
        currImg.draw(window,1,1)
        editbox.drawSelect()
        if showcursor or editmode or selectmode:
            window.addstr(editbox.y+1, editbox.x+1, info['char'], curses.color_pair(2))
        if showcopy:
            editbox.drawCopy()

        listwin.clear()
        listStart = max(imageIdx-12, 0)
        listEnd = min(listStart+24, len(images))
        for i, val in enumerate(images[listStart: listEnd]):
            listwin.addstr  ( i, 0, val[1][:16]
                            , (curses.A_STANDOUT if i == imageIdx else 0)
                            | (curses.color_pair(2) if val[0].unsaved else curses.color_pair(0))
                            )
        
        listwin.refresh()

        helpwin.clear()
       
        currCmds = selCommands if selectmode else commands 
        for i, cmds in enumerate(currCmds):
            for y, key in enumerate(cmds.keys()):
                helpwin.addch(y, i*20, key, curses.A_STANDOUT)
                helpwin.addstr(y, i*20+2, cmds[key][:])
        helpwin.refresh()

        window.refresh()
        cmdwin.refresh()
        cmdwin.clear()

        if editmode:
            editmode = editbox.edit(currImg, color)

        else: 
            cmd = window.getch()

            if selectmode:
                if editbox.select(cmd, currImg, color):
                    pass
                else:
                    selectmode = False
                    remakeWindows()
            else:
                if cmd == ord('i'):
                    editmode = True
                elif cmd == curses.KEY_RIGHT:
                    currImg.incFrame(1) 
                elif cmd == curses.KEY_LEFT:
                    currImg.incFrame(-1)
                elif cmd == curses.KEY_UP:
                    cycleImg(-1)
                elif cmd == curses.KEY_DOWN:
                    cycleImg(1)
                elif cmd == ord('q'):
                    if getConfirm(window, "Are you sure?", default = False):
                        break;
                elif cmd == ord('g'):
                    color = 1-color
                elif cmd == ord('s'):
                    currImg.save(currName)
                elif cmd == ord('l'):
                    currImg.load(currName)
                elif cmd == ord('a'):
                    drawalpha = not drawalpha
                elif cmd == ord('f'):
                    currImg.addFrame(currImg.cFrame)
                    currImg.cFrame += 1
                elif cmd == ord('b'):
                    editbox.bucket(currImg, color)
                elif cmd == ord('d'):
                    editbox.paste(currImg)
                elif cmd == ord('v'):
                    selectmode = True
                elif cmd == ord('\t'):
                    showcursor = not showcursor
                elif cmd == ord('1'):
                    showcopy = not showcopy
                elif cmd == ord('\\'):
                    editbox.pickChar()
                elif cmd == ord('p'):
                    play = not play
                elif cmd == ord('r'):
                    twidth, theight = getSize(window)
                    if twidth != None:
                        currImg.resize(0,twidth,0, theight)
                        remakeWindows()
                    #resize image here
                elif cmd == ord('n'):
                    name = getString(window, "ENTER NAME", "img/")
                    if name != None and validateName(name):
                        twidth, theight = getSize(window)
                        if twidth != None:
                            nImg = image.Image(theight, twidth)
                            images.append((nImg, name))

                elif cmd == ord('o'):
                    name = getString(window, "ENTER NAME", "img/")
                    if not os.path.exists(name):
                        #Do something about it
                        pass
                    else:
                        addFile(name)
                elif cmd == ord('c'):
                    if getConfirm(window, "Are you sure?"):
                        closeImg()
                elif cmd == ord('~'):
                    pdb.set_trace()
                    
                        

except:
    curses.endwin()
    raise
finally:
    curses.endwin()


