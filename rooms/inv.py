import game

class Room(game.Room):
    defVerbs = ["inv"]
    name = 'inv'
    desc = "This is not a room it is your inventory. What are you doing here?"

    def inv(self, cmd):
        invList = []
        for item in self.items.values():
            if not item.hidden:
                nameStr = item.name
                if item.qty > 1:
                    nameStr+="({})".format(item.qty)
                invList.append(nameStr)
        game.sayList(invList)

