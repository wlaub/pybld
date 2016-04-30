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
    locs =  { "upper left": {"right":"top", "down":"left"}
            , "top": {"left":"upper left", "down":"mid", "right":"upper right"}
            , "upper right": {"left":"top", "down":""}
            , "left": {"up":"upper left", "right":"mid", "down":"lower left"}
            , "mid": {"up":"top", "right":"right", "down":"bot", "left":"left"}
            , "right": {"up":"upper right", "down":"lower right","left":"mid"}
            , "lower left": {"up":"left", "right":"bot"}
            , "bot": {"up":"mid", "left":"lower left","right":"lower right"}
            , "lower right": {"left":"bot", "up":"right"}
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
    locs =  { "top": {"down":"mid"}
            , "left": {"right":"mid"}
            , "mid": {"up":"top", "right":"right", "down":"bot", "left":"left"}
            , "right": {"left":"mid"}
            , "bot": {"up":"mid"}
    }

