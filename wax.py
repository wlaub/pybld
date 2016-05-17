import time, sys, os, thread
import curses
from curses.textpad import Textbox
import pdb
import image, waxutil

images = []
imageIdx = 0

def addFile(filename, height=13, width = 60):
    global images, imageIdx
    tImg = image.Image(height, width)
    if os.path.exists(filename):
        tImg.load(filename)
    hist = image.History(tImg, name)
    images.append((hist, name))


for name in sys.argv[1:]:
    addFile(name)

def updateImage():
    global images, currName, currImg, currHist
    currName = images[imageIdx][1]
    currHist = images[imageIdx][0]
    currname = currHist.filename
    currImg = images[imageIdx][0].getImage()

updateImage()

editbox = None

def clamp(val, _min, _max):
    if val < _min:
        return _min
    if val > _max:
        return _max
    return val

def makeWindows():
    global window, cmdwin, editbox, helpwin, currImg
    
    window = curses.newwin(currImg.h+2,currImg.w+2,0,0)
    cmdwin = curses.newwin(2, 62, currImg.h+2, 0)
    helpwin = curses.newwin(7, 62, currImg.h+2+2, 0)

    window.keypad(1)

    if not editbox:
        editbox = waxutil.EditWindow(window.subwin(currImg.h, currImg.w, 1,1))
    editbox.reset(window.subwin(currImg.h, currImg.w, 1,1))


def clearWindows():
    global window, cmdwin, helpwin
    window.clear()
    window.refresh()
    cmdwin.clear()
    cmdwin.refresh()
    helpwin.clear()
    helpwin.refresh()

def remakeWindows():
    clearWindows()
    makeWindows()

def cycleImg(val):
    global imageIdx
    imageIdx += val
    if imageIdx < 0:
        imageIdx += len(images)
    if imageIdx >= len(images):
        imageIdx -= len(images)
    updateImage()
    clearWindows()
    makeWindows()

def closeImg():
    global imageIdx
    del images[imageIdx]
    imageIdx = clamp(imageIdx, 0, len(images)-1)
    updateImg()
    clearWindows()
    makeWindows()

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

def confirmUnsaved(curr = False):
    global window, images, currImg
    if curr:
        if currImg.unsaved:
            return getConfirm(window, "DISCARD CHANGES?", default = False)
    else:
        for hist, name in images:
            if hist.getImage().unsaved:
                return getConfirm(window, "DISCARD CHANGES?", default = False)
    return True

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
            window.border
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
                , "{mode} mode | Color: {color} | Char: {char} | 0x{cmd:04x} | {past}/{future}"
                ]


try:
    curses.initscr()
    curses.noecho()
    curses.mousemask(1)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_RED, -1)
    curses.init_pair(4, curses.COLOR_BLUE, -1)

    makeWindows()
    listwin = curses.newwin(24, 16, 0, 62)

    cmd = 0
    color = 0

    commands = waxutil.SymMap()
    selCommands = waxutil.SelMap()

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
                , 'length': currImg.frames[currImg.cFrame].length
                , 'past': len(currHist.buffer)
                , 'future': len(currHist.future)
                }
        info['char'] = currImg.frames[0].transcode(editbox.getChar())

        for i, val in enumerate(infoStrings): 
            cmdwin.addstr(i,0,val.format(**info))

        window.clear()
        if drawalpha:
            for y in range(currImg.h):
                window.addstr(y+1, 1, ' '*currImg.w, curses.color_pair(3))

        window.border()
        currHist.getImage().draw(window,1,1)
        editbox.drawSelect()
        if showcursor or editmode or selectmode:
            window.addstr(editbox.y+1, editbox.x+1, info['char'], curses.color_pair(2))
        if showcopy:
            editbox.drawCopy()

#        for key in curses.__dict__.keys():
#            if 'ACS' in key:
#                window.addch(curses.__dict__[key])

        listwin.clear()
        listStart = max(imageIdx-12, 0)
        listEnd = min(listStart+24, len(images))
        for i, val in enumerate(images[listStart: listEnd]):
            img = val[0].getImage()
            name = val[0].filename
            listwin.addstr  ( i, 0, name[:16]
                            , (curses.A_STANDOUT if i == imageIdx else 0)
                            | (curses.color_pair(2) if val[0].unsaved else curses.color_pair(0))
                            )
        
        listwin.refresh()

        helpwin.clear()

        currCmds = selCommands if selectmode else commands
        currCmds.draw(helpwin)      

        helpwin.refresh()

        window.refresh()
        cmdwin.refresh()
        cmdwin.clear()

        if editmode:
            editmode = editbox.edit(currHist, color)

        else: 
            cmd = window.getch()

            if selectmode:
                if editbox.select(cmd, currHist, color):
                    pass
                else:
                    selectmode = False
                    remakeWindows()
            else:
                name, _, _ = commands.parseCommand(cmd)
                if name == 'edit':
                    editmode = True
                elif name == 'next frame':
                    currImg.incFrame(1) 
                elif name == 'prev frame':
                    currImg.incFrame(-1)
                elif name == 'prev img':
                    cycleImg(-1)
                elif name == 'next img':
                    cycleImg(1)
                elif name == 'undo':
                    currHist.undo()
                elif name == 'redo':
                    currHist.redo()
                elif name == 'quit':
                    if confirmUnsaved():
                        break;
                elif name == 'color':
                    color = 1-color
                elif name == 'save':
                    currHist.save()
                elif name == 'load':
                    if confirmUnsaved(True):
                        currHist.load()
                elif name == 'alpha':
                    drawalpha = not drawalpha
                elif name == 'frame':
#HERE
                    currImg.addFrame(currImg.cFrame)
                    currImg.cFrame += 1
                elif name == 'bucket':
                    editbox.bucket(currHist, color)
                elif name == 'paste':
                    editbox.paste(currHist)
                elif name == 'select':
                    selectmode = True
                elif name == 'cursor':
                    showcursor = not showcursor
                elif name == 'scopy':
                    showcopy = not showcopy
                elif name == 'char':
                    editbox.pickChar()
                elif name == 'play':
                    play = not play
                elif name == 'resize':
#HERE
                    twidth, theight = getSize(window)
                    if twidth != None:
                        currImg.resize(0,twidth,0, theight)
                        remakeWindows()
                elif name == 'new':
                    name = getString(window, "ENTER NAME", "img/")
                    if name != None and validateName(name):
                        twidth, theight = getSize(window)
                        if twidth != None:
                            addFile(name, theight, twidth)
#                            nImg = image.Image(theight, twidth)
#                            images.append((nImg, name))
                elif name == 'open':
                    name = getString(window, "ENTER NAME", "img/")
                    if not os.path.exists(name):
                        getConfirm(window, "Does not exist", "ok", "OK")
                    else:
                        addFile(name)
                elif name == 'up':
                    editbox.moveCursor(-1,0)
                elif name == 'down':
                    editbox.moveCursor(1,0)
                elif name == 'left':
                    editbox.moveCursor(0,-1)
                elif name == 'right':
                    editbox.moveCursor(0,1)
                elif name == 'close':
                    if confirmUnsaved(True):
                        closeImg()
                elif name == 'debug':
                    pdb.set_trace()
                    
                        

except:
    curses.endwin()
    raise
finally:
    curses.endwin()


