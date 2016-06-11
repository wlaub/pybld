import curses
import os, sys, time, thread
import pdb

import image

class Manager():

    def __init__(self):
        self.images = {}

    def getImage(self, name):
        if not name in self.images.keys():
            nImage = image.Image(filename = name)
            self.images[name] = nImage
        return self.images[name]

    def loadImage(self, name):
        """
        Looks up the given filename and loads the image if
        it's not already loaded.
        """
        pass

def loop(obj):
    obj.frame = 0

def oneshot(obj):
    obj.frame -=1
    obj.stopped=True

class Sprite():

    def __init__(self, name, y, x, layer=0, callback = loop):
        self.y = y
        self.x = x
        self.layer = layer
        self.name = name
        self.frame = 0
        self.t = 0
        self.callback = callback
        self.stopped = False
        pass

    def change(self, name):
        self.name = name
        self.frame = 0
        self.t = 0

    def tick(self, man):
        if self.stopped:
            return
        img = man.getImage(self.name)
        self.t += 1
        if self.t == img.frames[self.frame].length:
            self.t = 0
            self.frame += 1
            if self.frame == len(img.frames):
                self.callback(self)

        pass

    def draw(self, man, window):
        img = man.getImage(self.name)
        img.frames[self.frame].draw(window, self.y, self.x)
        pass


class EmptyRenderer():
    def __init__(self, interface = None, rate = .333):
        pass
    def play(self, playing):
        pass
    def addSprite(self, sprite):
        pass
    def removeSprite(self, sprite):
        pass
    def clear(self):
        pass


class Renderer():

    def __init__(self, interface, rate = .333):
        self.win = interface.getImgWin()
        self.win.leaveok(1)
        self.rate = rate
        self.playing = True
        self.sprites = {}
        self.man = Manager()
        #spawn thread?
        thread.start_new_thread(self.thread,())
        

    def thread(self):
        while 1:
            time.sleep(self.rate)
            if self.playing:
                self.tick(self.rate)
                self.draw()
                
    
    def tick(self, delta):
        for layer in self.sprites.values():
            for sprite in layer:
                sprite.tick(self.man)

    def draw(self):
        self.win.clear()
        self.win.hline(self.win.getmaxyx()[0]-1, 0, curses.ACS_HLINE, 60)
        keys = self.sprites.keys()
        keys.sort()
        for layer in keys:
            for sprite in self.sprites[layer]:
                sprite.draw(self.man, self.win) 
        self.win.refresh()

    def play(self, playing):
        self.playing = playing

    def addSprite(self, sprite):
        """
        Add the sprite to the render dictionary
        """
        if not sprite.layer in self.sprites.keys():
            self.sprites[sprite.layer] = []
        if not sprite in self.sprites[sprite.layer]:
            self.sprites[sprite.layer].append(sprite)

    def clear(self):
        """
        Clears the current draw dictionary so nothing
        will be drawn.
        """
        self.sprites = {}
        pass


