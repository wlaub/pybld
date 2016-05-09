import time
import curses
import pdb
import image

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
test = image.Image()
test.load(filename)

editmode = False

try:
    curses.initscr()
    window = curses.newwin(test.h+2,test.w+2,0,0)
    window.border()

    cmdwin = curses.newwin(3, 60, test.h+2, 0)

    curses.noecho()
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)

 
    cmd = 0

    while 1:
        cmdStr =    [ "{mode} mode".format(mode = "Edit" if editmode else "Command")
                    ,  "{name}: {w}x{h} - {cmd:04x}".format(w = test.w, h = test.h, cmd=cmd, name = filename)
                    , "i: edit | q: quit" 
                    ]


        for i, val in enumerate(cmdStr): 
            cmdwin.addstr(i,0,val)
        
        test.draw(window,1,1)        
        window.refresh()
        cmdwin.refresh()
        cmdwin.clear()

        cmd = window.getch()

        if editmode:
            if cmd == 0x1b:
                editmode = False
        else:      
            if cmd == ord('i'):
                editmode = True
            if cmd == ord('q'):
                break;



except:
    curses.endwin()
    raise
finally:
    curses.endwin()


