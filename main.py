import random, os, time, copy
import threading
from getkey import getkey, keys

#--------------------------------------#
# SETTINGS FOR THE GAME YOU CAN CHANGE #
#                 ↓                    #
#--------------------------------------#

icons = {
    1: "⬜",
    2: "🟩",
    3: "🟨",
    4: "🟧",
    5: "🟦",
    6: "🟪",
    7: "🟫",
    8: "🟥",
    9: "⬛",
    10: "🍎",
    11: "🥝",
    12: "🍓",
    13: "🍈",
    14: "🍍",
    15: "🥭",
    16: "🍋",
    17: "🍑",
    18: "🍊",
    19: "🍅",
    20: "🥑",
    21: "🍉",
    22: "🍒",
    23: "🍌",
    24: "🍇",
    25: "🍐",
    26: "🍆"
}

# Change the first number to change the icon
presets = { #  ↓↓
    "fruit":  [21, "fruit", -1],
    "player": [4, "player", -1],
    "block":  [9, "block", -1],
    "tail":    3
}

# I will be adding more of these settings later.
# Some also don't work
settings = {
    "canDie": True, # You don't die to your tail.
    "manualInput": False # Superhot rules. 
}

# Please, only use odd numbers. I built the math around that.
# Even numbers might cause a crash
x, y = 9, 9

# Anything less than this will be choppy.
# This also only works in auto mode.
delay = .13

#--------------------------------------#
#                 ↑                    #
# SETTINGS FOR THE GAME YOU CAN CHANGE #
#--------------------------------------#

inputConvert = {
    keys.W: -1,
    keys.S: 1,
    keys.A: -1,
    keys.D: 1
}

def displayBoard(board):
    global points
    board = ''.join([icons[cell[2][0]] + '\n' if (count + 1) == len(row) else icons[cell[2][0]]
            for row in board for count, cell in enumerate(row)])
    print(f"{points}\n{board}")

def placeBerry(board):
    dummy = copy.deepcopy(board)
    """
    Places a random berry on the given board.
    """
    while True:
        x, y = len(board), len(board[0])
        randX, randY = random.randint(0, x - 1), random.randint(0, y - 1)
        try:
            if dummy[randY][randX][2][1] != "block":
                dummy[randY].remove(dummy[randY][randX])
                continue
            else:
                board[randY][randX][2] = presets["fruit"]
                return board
        except IndexError:
            continue

def makeBoard(x, y):
    board = [[[x, y, presets['block']] for x in range(x)] for y in range(y)]
    # placing the player
    board[int((y / 2) + .5) - 1][int((x / 2) + .5) - 3][2] = presets["player"]
    # placing the fruit
    board[int((y / 2) + .5) - 1][int((x / 2) + .5)][2] = presets["fruit"]
    return [board, (int((y / 2) + .5) - 1, int((x / 2) + .5) - 3)]

def degradeTail(board):
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            if cell[2][1] == "tail":
                life = board[y][x][2][2]
                if life - 1 < 1:
                    board[y][x][2] = presets["block"]
                else:
                    board[y][x][2][2] = life - 1

def moveLogic(board, start, points, x:int, y:int, xMove:int=0, yMove:int=0):
    Start = board[start[0]][start[1]][2]

    if ((start[0] + yMove < 0) or (start[0] + yMove > y - 1)) or ((start[1] + xMove < 0) or (start[1] + xMove > x - 1)):
        return False
    
    Next = board[start[0] + yMove][start[1] + xMove][2]
    
    if settings["canDie"]:
        if Next[1] == "tail":
            return False
    else:
        Next = board[start[0] + yMove][start[1] + xMove][2]

    if Next[1] == "fruit":
        board[start[0] + yMove][start[1] + xMove][2] = Start
        board[start[0]][start[1]][2] = [presets["tail"], "tail", points + 4]
        board = placeBerry(board)
        return [board, 1]
    else:
        board[start[0] + yMove][start[1] + xMove][2] = Start
        board[start[0]][start[1]][2] = [presets["tail"], "tail", points + 3]
        degradeTail(board)
        return [board, 0]

def autoMove():
    global playerCoords, points, lastMove, board, delay, alive
    while alive:
        time.sleep(delay)
        if lastMove in [keys.W, keys.S]:
            AUTO = moveLogic(board, playerCoords, points, x, y, yMove= inputConvert[lastMove])
            playerCoords = (playerCoords[0] + inputConvert[lastMove], playerCoords[1])
        elif lastMove in [keys.A, keys.D]:
            AUTO = moveLogic(board, playerCoords, points, x, y, xMove= inputConvert[lastMove])
            playerCoords = (playerCoords[0], playerCoords[1] + inputConvert[lastMove])
        else:
            continue

        if not AUTO:
            alive = False
            break
        else:
            aBoard = AUTO[0]
            points += AUTO[1]
            os.system("clear")
            displayBoard(aBoard)

playing = True

os.system("clear")
while playing:
    points = 0
    tries = 0

    print("Press any button the continue..."); getkey()
    os.system("clear")
    
    MAKE = makeBoard(x, y)
    board = MAKE[0]
    playerCoords = MAKE[1]
    lastMove = None
    didSomething = True

    alive = True
    if not settings["manualInput"]:
        threading.Thread(target=autoMove).start()
    while alive:
        if didSomething:
            os.system("clear")
            displayBoard(board)
        didSomething = False
        move = getkey()

        if lastMove == move and not settings['manualInput']:
            continue
        
        if move == keys.W and lastMove != keys.S:
            if not settings['manualInput']:
                lastMove = move
                continue
            MOVED = moveLogic(board, playerCoords, points, x, y, yMove=-1)
            playerCoords = (playerCoords[0] - 1, playerCoords[1])
        elif move == keys.S and lastMove != keys.W:
            if not settings['manualInput']:
                lastMove = move
                continue
            MOVED = moveLogic(board, playerCoords, points, x, y, yMove=1)
            playerCoords = (playerCoords[0] + 1, playerCoords[1])
        elif move == keys.A and lastMove != keys.D:
            if not settings['manualInput']:
                lastMove = move
                continue
            MOVED = moveLogic(board, playerCoords, points, x, y, xMove=-1)
            playerCoords = (playerCoords[0], playerCoords[1] - 1)
        elif move == keys.D and lastMove != keys.A:
            if not settings['manualInput']:
                lastMove = move
                continue
            MOVED = moveLogic(board, playerCoords, points, x, y, xMove=1)
            playerCoords = (playerCoords[0], playerCoords[1] + 1)
        else:
            continue

        didSomething = True
        lastMove = move

        if type(MOVED) is bool:
            alive = False
            break
        else:   
            board = MOVED[0]
            points += MOVED[1]