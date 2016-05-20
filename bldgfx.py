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


class Sprite():

    def __init__(self, name, y, x, layer=0):
        self.y = y
        self.x = x
        self.layer = layer
        self.name = name
        self.frame = 0
        self.t = 0
        pass

    def tick(self, man):
        img = man.getImage(self.name)
        self.t += 1
        if self.t == img.frames[self.frame].length:
            self.t = 0
            self.frame += 1
            if self.frame == len(img.frames):
                self.frame = 0

        pass

    def draw(self, man, window):
        img = man.getImage(self.name)
        img.frames[self.frame].draw(window, self.y, self.x)
        pass


class Renderer():

    def __init__(self, window, rate = .333):
        self.win = window
        self.rate = rate
        self.play = True
        self.sprites = {}
        self.man = Manager()
        #spawn thread?
        thread.start_new_thread(self.thread,())


    def thread(self):
        while 1:
            time.sleep(self.rate)
            if self.play:
                self.tick(self.rate)
            self.draw()

    def tick(self, delta):
        for layer in self.sprites.values():
            for sprite in layer:
                sprite.tick(self.man)

    def draw(self):
        self.win.clear()
        self.win.hline(self.win.getmaxyx()[0]-1, 0, curses.ACS_HLINE, 60)
        self.win.leaveok(1)
        keys = self.sprites.keys()
        keys.sort()
        for layer in keys:
            for sprite in self.sprites[layer]:
                sprite.draw(self.man, self.win) 
        self.win.refresh()

    def play(self, playing):
        self.play = playing

    def addSprite(self, sprite):
        """
        Add the sprite to the render dictionary
        """
        if not sprite.layer in self.sprites.keys():
            self.sprites[sprite.layer] = []
        if not sprite in self.sprites[sprite.layer]:
            self.sprites[sprite.layer].append(sprite)

    def removeSprite(self, sprite):
        """
        Removes the sprite from the render dictionary
        """
        try:
            self.sprites[sprite.layer].remove(sprite)
        except:
            pass

    def clear(self):
        """
        Clears the current draw dictionary so nothing
        will be drawn.
        """
        self.sprites = {}
        pass

    def refresh(self):
        """
        Replaces the current draw dictionary with the
        buffer.
        """
        pass
