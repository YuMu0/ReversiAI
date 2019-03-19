import pygame, sys, random
from pygame.locals import *
import numpy as np
BACKGROUNDCOLOR = (255, 255, 255)
BLACK = (255, 255, 255)
BLUE = (0, 0, 255)
CELLWIDTH = 80
CELLHEIGHT = 80
PIECEWIDTH = 47
PIECEHEIGHT = 47
BOARDX = 55
BOARDY = 55
FPS = 40
# alpha_beta减枝
# 传进来如果flag是True 那么就是computer下
#传进来flag为false 那么就是player下
def alpha_beta(board,computerTile,playerTile,flag,alpha,beta,depth):
    bestValue = -1000000
    if flag is True:
        Tile = computerTile
    else:
        Tile = playerTile
    possible = getValidMoves(board,Tile)
    for x,y in possible:
        copyBoard = getBoardCopy(board)
        makeMove(copyBoard,Tile,x,y)
        if depth <= 1:
            Value = getEvaluationOfBoard(copyBoard)[Tile]
        else:
            Value = -alpha_beta(copyBoard,computerTile,playerTile,not flag,-beta,-alpha,depth-1)
        if Value >= beta:
            return Value
        if Value > bestValue:
            bestValue = Value
            if Value > alpha:
                alpha = Value

    return bestValue

# 退出
def terminate():
    pygame.quit()
    sys.exit()
# 重置棋盘
def resetBoard(board):
    for x in range(8):
        for y in range(8):
            board[x][y] = 'none'
    # Starting pieces:
    board[3][3] = 'black'
    board[3][4] = 'white'
    board[4][3] = 'white'
    board[4][4] = 'black'
# 开局时建立新棋盘

def getNewBoard():
    board = []
    for i in range(8):
        board.append(['none'] * 8)
    return board
# 是否是合法走法
def isValidMove(board, tile, xstart, ystart):
    # 如果该位置已经有棋子或者出界了，返回False
    if not isOnBoard(xstart, ystart) or board[xstart][ystart] != 'none':
        return False
    # 临时将tile 放到指定的位置
    board[xstart][ystart] = tile
    if tile == 'black':
        otherTile = 'white'
    else:
        otherTile = 'black'
    # 要被翻转的棋子
    tilesToFlip = []
    for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
        x, y = xstart, ystart
        x += xdirection
        y += ydirection
        if isOnBoard(x, y) and board[x][y] == otherTile:
            x += xdirection
            y += ydirection
            if not isOnBoard(x, y):
                continue
            # 一直走到出界或不是对方棋子的位置
            while board[x][y] == otherTile:
                x += xdirection
                y += ydirection
                if not isOnBoard(x, y):
                    break
            # 出界了，则没有棋子要翻转OXXXXX
            if not isOnBoard(x, y):
                continue
            # 是自己的棋子OXXXXXXO
            if board[x][y] == tile:
                while True:
                    x -= xdirection
                    y -= ydirection
                    # 回到了起点则结束
                    if x == xstart and y == ystart:
                        break
                    # 需要翻转的棋子
                    tilesToFlip.append([x, y])
    # 将前面临时放上的棋子去掉，即还原棋盘
    board[xstart][ystart] = 'none'  # restore the empty space
    # 没有要被翻转的棋子，则走法非法。翻转棋的规则。
    if len(tilesToFlip) == 0:  # If no tiles were flipped, this is not a valid move.
        return False
    return tilesToFlip
# 是否出界
def isOnBoard(x, y):
    return x >= 0 and x <= 7 and y >= 0 and y <= 7
# 获取可落子的位置
def getValidMoves(board, tile):
    validMoves = []
    for x in range(8):
        for y in range(8):
            if isValidMove(board, tile, x, y) != False:
                validMoves.append([x, y])
    # return []
    return validMoves
# 获取棋盘上黑白双方的棋子数
def getEvaluationOfBoard(board):
    BoardBlack = np.zeros((8,8))
    BoardWhite = np.zeros((8,8))
    Vmap = np.array([[500, -25, 10, 5, 5, 10, -25, 500], [-25, -45, 1, 1, 1, 1, -45, -25], [10, 1, 3, 2, 2, 3, 1, 10],
                     [5, 1, 2, 1, 1, 2, 1, 5], [5, 1, 2, 1, 1, 2, 1, 5], [10, 1, 3, 2, 2, 3, 1, 10],
                     [-25, -45, 1, 1, 1, 1, -45, -25], [500, -25, 10, 5, 5, 10, -25, 500]])
    for x in range(8):
        for y in range(8):
            if board[x][y] == 'black':
                BoardBlack[x][y] = 1
            if board[x][y] == 'white':
                BoardWhite[x][y] = 1

    print(BoardWhite,end='**************')
    print(BoardBlack,end='$$$$$$$$$$$$$$$$$$$')
    BoardBlack = BoardBlack * Vmap
    BoardWhite = BoardWhite * Vmap
    BlackValue = np.sum(BoardBlack)
    WhiteValue = np.sum(BoardWhite)
    return {'black': BlackValue, 'white': WhiteValue}

def getScoreOfBoard(board):
    xscore = 0
    oscore = 0
    for x in range(8):
        for y in range(8):
            if board[x][y] == 'black':
                xscore += 1
            if board[x][y] == 'white':
                oscore += 1
    return {'black': xscore, 'white': oscore}

# 谁先走

def whoGoesFirst():
    if random.randint(0, 1) == 0:

        return 'computer'

    else:

        return 'player'


# 将一个tile棋子放到(xstart, ystart)

def makeMove(board, tile, xstart, ystart):
    tilesToFlip = isValidMove(board, tile, xstart, ystart)

    if tilesToFlip == False:
        return False

    board[xstart][ystart] = tile

    for x, y in tilesToFlip:
        board[x][y] = tile

    return True


# 复制棋盘

def getBoardCopy(board):
    dupeBoard = getNewBoard()
    for x in range(8):
        for y in range(8):
            dupeBoard[x][y] = board[x][y]

    return dupeBoard


# 是否在角上

def isOnCorner(x, y):
    return (x == 0 and y == 0) or (x == 7 and y == 0) or (x == 0 and y == 7) or (x == 7 and y == 7)


# 电脑走法，AI

def getComputerMove(board, computerTile):
    # 获取所以合法走法
    flag = True
    bestMove = []
    possibleMoves = getValidMoves(board, computerTile)
    # 打乱所有合法走法
    sscore = []
    random.shuffle(possibleMoves)
    # [x, y]在角上，则优先走，因为角上的不会被再次翻转
    for x, y in possibleMoves:
        if isOnCorner(x, y):
            return [x, y]
    bestScore = -100000000
    for x, y in possibleMoves:
        dupeBoard = getBoardCopy(board)
        makeMove(dupeBoard, computerTile, x, y)
        #score = getScoreOfBoard(dupeBoard)[computerTile]
        score = alpha_beta(dupeBoard,computerTile,playerTile,flag,-1000000,1000000,3)
        sscore.append(score)
        print(sscore)
        if score > bestScore:
            bestMove = [x, y]
            bestScore = score
    # for x, y in possibleMoves:
    #     dupeBoard = getBoardCopy(board)
    #     makeMove(dupeBoard, computerTile, x, y)
    #     # 按照分数选择走法，优先选择翻转后分数最多的走法
    #     score = getScoreOfBoard(dupeBoard)[computerTile]
    #     if score > bestScore:
    #         bestMove = [x, y]
    #         bestScore = score
    return bestMove
# 是否游戏结束

def isGameOver(board):
    for x in range(8):
        for y in range(8):
            if board[x][y] == 'none':
                return False

    return True


# 初始化
pygame.init()
mainClock = pygame.time.Clock()
# 加载图片
boardImage = pygame.image.load('board.png')
boardRect = boardImage.get_rect()
blackImage = pygame.image.load('black.png')
blackRect = blackImage.get_rect()
whiteImage = pygame.image.load('white.png')
whiteRect = whiteImage.get_rect()
basicFont = pygame.font.SysFont(None, 48)
gameoverStr = 'Game Over Score '
mainBoard = getNewBoard()
resetBoard(mainBoard)
turn = whoGoesFirst()
if turn == 'player':
    playerTile = 'black'
    computerTile = 'white'
else:
    playerTile = 'white'
    computerTile = 'black'
print(turn)
# 设置窗口

windowSurface = pygame.display.set_mode((boardRect.width, boardRect.height))
pygame.display.set_caption('黑白棋')
gameOver = False
# 游戏主循环
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            terminate()
        if gameOver == False and turn == 'player' and event.type == MOUSEBUTTONDOWN and event.button == 1:
            x, y = pygame.mouse.get_pos()
            col = int((x - BOARDX) / CELLWIDTH)
            row = int((y - BOARDY) / CELLHEIGHT)
            if makeMove(mainBoard, playerTile, col, row) == True:
                if getValidMoves(mainBoard, computerTile) != []:
                    turn = 'computer'
    windowSurface.fill(BACKGROUNDCOLOR)
    windowSurface.blit(boardImage, boardRect, boardRect)
    if (gameOver == False and turn == 'computer'):
        x, y = getComputerMove(mainBoard, computerTile)
        makeMove(mainBoard, computerTile, x, y)
        savex, savey = x, y
        # 玩家没有可行的走法了
        if getValidMoves(mainBoard, playerTile) != []:
            turn = 'player'
    windowSurface.fill(BACKGROUNDCOLOR)
    windowSurface.blit(boardImage, boardRect, boardRect)
    for x in range(8):
        for y in range(8):
            rectDst = pygame.Rect(BOARDX + x * CELLWIDTH + 2, BOARDY + y * CELLHEIGHT + 2, PIECEWIDTH, PIECEHEIGHT)
            if mainBoard[x][y] == 'black':
                windowSurface.blit(blackImage, rectDst, blackRect)
            elif mainBoard[x][y] == 'white':
                windowSurface.blit(whiteImage, rectDst, whiteRect)
    if isGameOver(mainBoard):
        scorePlayer = getScoreOfBoard(mainBoard)[playerTile]
        scoreComputer = getScoreOfBoard(mainBoard)[computerTile]
        outputStr = gameoverStr + str(scorePlayer) + ":" + str(scoreComputer)
        text = basicFont.render(outputStr, True, BLACK, BLUE)
        textRect = text.get_rect()
        textRect.centerx = windowSurface.get_rect().centerx
        textRect.centery = windowSurface.get_rect().centery
        windowSurface.blit(text, textRect)
    pygame.display.update()
    mainClock.tick(FPS)
