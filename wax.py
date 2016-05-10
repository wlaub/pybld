import time, sys, os
import curses
from curses.textpad import Textbox
import pdb
import image, waxutil

"""
test = image.Frame()
data = "\x01\x03\x03\x03\x03\x02AB\x02\x81\xc1\xc2\x81\x20\x20\x20\x20"
data = ['\x01']
data.extend(['\x03']*60*3)
data.extend(['\x02']*60*3)
data.extend(['\x01']*60*3)
data.extend(['\x00']*60*3)


data = ''.join(data)
test.load(data, 13,60)


filename = "img/test.bmi"
timg = image.Image()
timg.frames.append(test)
timg.save(filename)
"""

images = []
imageIdx = 0

for name in sys.argv[1:]:
    tImg = image.Image()
    if os.path.exists(name):
        tImg.load(name)
    images.append((tImg, name))

currName = images[imageIdx][1]
currImg = images[imageIdx][0]

def cycleImg(val):
    imageIdx += val
    if imageIdx < 0:
        imageIdx += len(images)
    if imageIdx >= len(images):
        imageIdx -= len(images)
    currName = images[imageIdx][1]
    currImg = images[imageIdx][0]
    #resize editbox and stuff


editmode = False
selectmode = False
drawalpha =False

infoStrings =   [ "{name} | {w} x {h} | ({x},{y}) | {frame}/{frameCount} | {length}"
                , "{mode} mode | Color: {color}"
                , "i: edit | q: quit | 0x{cmd:04x}"
                ]

commands =  { 'q': 'quit'
            , 'i': 'edit'
            , 'f': 'new frame'
            , 's': 'save'
            , 'l': 'load'
            , 'o': 'open'
            , 'n': 'new'
            , 'a': 'show alpha'
            , 'p': 'play/pause'
            , '->': 'next frame'
            , '<-': 'prev frame'
            , 'v': 'select'
            }
selCommands =   { 'c': 'crop'
                , 'f': 'fill' 
                }

try:
    curses.initscr()
    window = curses.newwin(currImg.h+2,currImg.w+2,0,0)
    window.border()

    cmdwin = curses.newwin(3, 60, currImg.h+2, 0)

    curses.noecho()
    curses.mousemask(1)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)

    window.keypad(1)

    editbox = waxutil.EditWindow(window.subwin(currImg.h, currImg.w, 1,1))

    cmd = 0
    color = 0

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
                }

        for i, val in enumerate(infoStrings): 
            cmdwin.addstr(i,0,val.format(**info))

        window.clear()
        if drawalpha:
            for y in range(currImg.h):
                window.addstr(y+1, 1, ' '*currImg.w, curses.color_pair(2))

        window.border()
        currImg.draw(window,1,1)
        editbox.drawSelect()
        if editmode or selectmode:
            window.addch(editbox.y+1, editbox.x+1, '*')
        window.refresh()
        cmdwin.refresh()
        cmdwin.clear()

        if editmode:
            editmode = editbox.edit(currImg, color)

        else: 
            cmd = window.getch()

            if selectmode:
                if editbox.select(cmd):
                    pass
                else:
                    selectmode = False

            else:
                if cmd == ord('i'):
                    editmode = True
                elif cmd == curses.KEY_RIGHT:
                    currImg.incFrame(1) 
                elif cmd == curses.KEY_LEFT:
                    currImg.incFrame(-1)
                elif cmd == ord('q'):
                    break;
                elif cmd == ord('g'):
                    color = 1-color
                elif cmd == ord('s'):
                    currImg.save(filename)
                elif cmd == ord('l'):
                    currImg.load(filename)
                elif cmd == ord('a'):
                    drawalpha = not drawalpha
                elif cmd == ord('f'):
                    currImg.addFrame(test.cFrame)
                    currImg.cFrame += 1
                elif cmd == ord('v'):
                    selectmode = True

except:
    curses.endwin()
    raise
finally:
    curses.endwin()


