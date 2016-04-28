import game

class Map():
    #Up right down left
    locs = {
    }

    strings = {
    "fail": "You can't go any farther {0}",
    "pass": "You walk to the {0}. "
    }

    def go(self, _from, _dir):
        _next = None
        if _dir in self.locs[_from].keys():
            _next = self.locs[_from][_dir]
        if _next == None:
            game.say(self.strings['fail'].format(_dir)) 
            return None
        game.sayBit(self.strings['pass'].format(_dir))
        return _next


class HalfMap(Map):
    #01
    locs = {
    "left": {"right":"right"},
    "right": {"left":"left"} 
    }    


class SquareMap(Map):
    #01
    #23
    locs = {
    "upper left": {"right": "upper right", "down": "lower left"},
    "upper right": {"left": "upper left", "down": "lower right"},
    "lower left": {"right": "lower right", "up": "upper left"},
    "lower right": {"left": "lower left", "up": "upper right"},
    }

class GridMap(Map):
    #012
    #345
    #678
    locs = {
    }

class HorMap(Map):
    #012
    locs = {
    "left": {"right":"mid"},
    "mid":{"left": "left", "right":"right"},
    "right": {"left":"mid"} 
    }

class VertMap(Map):
    #1
    #2
    #3
    locs = {
    "top": {"down":"mid"},
    "mid":{"down":"bot","up":"top"},
    "bot":{"up":"mid"}
    }

class PlusMap(Map):
    # 0
    #123
    # 4
    locs = {

    }

