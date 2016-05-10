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


filename = "img/test.bmi"

if len(sys.argv) > 1:
    filename = sys.argv[1]



test = image.Image()

if not os.path.exists(filename):
    test.save(filename)

test.load(filename)

editmode = False
drawalpha =False

infoStrings =   [ "{mode} mode | Color: {color}"
                , "{name} | {w} x {h} | ({x},{y}) | {frame}/{frameCount} | {length}"
                , "i: edit | q: quit | 0x{cmd:04x}"
                ]

try:
    curses.initscr()
    window = curses.newwin(test.h+2,test.w+2,0,0)
    window.border()

    cmdwin = curses.newwin(3, 60, test.h+2, 0)

    curses.noecho()
    curses.mousemask(1)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)

    window.keypad(1)

    editbox = waxutil.EditWindow(window.subwin(test.h, test.w, 1,1))

    cmd = 0
    color = 0

    while 1:

        info =  { 'mode': "Edit" if editmode else "command"
                , 'color': "Green" if color else "normal"
                , 'cmd': cmd
                , 'name': filename
                , 'w': test.w
                , 'h': test.h
                , 'x': editbox.x
                , 'y': editbox.y
                , 'frame': test.cFrame+1
                , 'frameCount': len(test.frames)
                , 'length': test.frames[test.cFrame].length
                }

        for i, val in enumerate(infoStrings): 
            cmdwin.addstr(i,0,val.format(**info))

        window.clear()
        if drawalpha:
            for y in range(test.h):
                window.addstr(y+1, 1, ' '*test.w, curses.color_pair(2))

        window.border()
        test.draw(window,1,1)        
        if editmode:
            window.addch(editbox.y+1, editbox.x+1, '*')
        window.refresh()
        cmdwin.refresh()
        cmdwin.clear()

        if editmode:
            editmode = editbox.edit(test, color)

        else: 
            cmd = window.getch()

            if cmd == ord('i'):
                editmode = True
            elif cmd == curses.KEY_RIGHT:
                test.incFrame(1) 
            elif cmd == curses.KEY_LEFT:
                test.incFrame(-1)
            elif cmd == ord('q'):
                break;
            elif cmd == ord('g'):
                color = 1-color
            elif cmd == ord('s'):
                test.save(filename)
            elif cmd == ord('l'):
                test.load(filename)
            elif cmd == ord('a'):
                drawalpha = not drawalpha
            elif cmd == ord('n'):
                test.addFrame(test.cFrame)
                test.cFrame += 1

except:
    curses.endwin()
    raise
finally:
    curses.endwin()


