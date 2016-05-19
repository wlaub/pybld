import curses
import os, sys, time, thread
import pdb

import image

class Manager():

    def __init__(self):
        pass

    def getImage(self, name):
        pass

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
        pass

    def tick(self, delta):
        pass

    def draw(self, window):
        pass


class Renderer():

    def __init__(self, window, rate = .333):
        self.win = window
        self.rate = rate
        self.play = True
        #spawn thread?

    def play(self, playing):
        self.play = playing

    def addSprite(self, sprite):
        """
        Adds a sprite to the buffer so it will be drawn
        after the next call to refresh().
        """
        pass

    def clear(self):
        """
        Clears the current draw dictionary so nothing
        will be drawn.
        """
        pass

    def refresh(self):
        """
        Replaces the current draw dictionary with the
        buffer.
        """
        pass
