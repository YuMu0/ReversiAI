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
def mtd(board,computerTile,playerTile,flag,alpha,beta,test,depth):
    bestValue = -1000000
    while alpha < beta:
        bestValue = alpha_beta(board,computerTile,playerTile,flag,test-1,test,depth)
        if bestValue < test:
            beta = bestValue
            test = bestValue
        else:
            alpha = bestValue
            test = bestValue + 1
    return bestValue
def pvs(board,computerTile,playerTile,flag,alpha,beta,depth):
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
        elif bestValue == -1000000:
            Value = -pvs(copyBoard,computerTile,playerTile,not flag,-beta,-alpha,depth-1)
        else:
            Value = -pvs(copyBoard,computerTile,playerTile,not flag,-alpha-1,-alpha,depth-1)
            if Value >alpha and Value < beta:
                alpha = Value
                Value = -pvs(copyBoard, computerTile, playerTile, not flag, -beta, -alpha, depth - 1)
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

# 初始化棋盘

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

# 是否是合法走法，返回false或者此走法能够被翻转的棋子位置

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

# 获取可落子的位置，返回这些坐标，并作出标记

def getValidMoves(board, tile):
    validMoves = []
    for x in range(8):
        for y in range(8):
            if isValidMove(board, tile, x, y) != False:
                validMoves.append([x, y])
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


# 谁先走，返回turn
def whoGoesFirst():
    return 'player'
    # if random.randint(0, 1) == 0:
    #     return 'computer'
    # else:
    #     return 'player'

# 将一个tile棋子放到(xstart, ystart)，返回True或False，并在board中修改值


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


# 电脑走法，AI，返回最佳走法的坐标

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
    bestScore = -1
    for x, y in possibleMoves:
        dupeBoard = getBoardCopy(board)
        makeMove(dupeBoard, computerTile, x, y)
        #score = getScoreOfBoard(dupeBoard)[computerTile]
        #score = pvs(dupeBoard,computerTile,playerTile,flag,-1000000,1000000,3)
        score = mtd(dupeBoard,computerTile,playerTile,flag,-1000000,1000000,10,3)
        sscore.append(score)
        print(sscore)
        if score > bestScore:
            bestMove = [x, y]
            bestScore = score

    return bestMove


# 是否游戏结束

def isGameOver(board):
    for x in range(8):
        for y in range(8):
            if board[x][y] == 'none':
                return False

    return True

# 画出棋子，无返回值
def drawTile(board):
    for x in range(8):
        for y in range(8):
            rectDst = pygame.Rect(BOARDX + x * CELLWIDTH + 2, BOARDY + y * CELLHEIGHT + 2, PIECEWIDTH, PIECEHEIGHT)
            if mainBoard[x][y] == 'black':
                windowSurface.blit(blackImage, rectDst, blackRect)
            elif mainBoard[x][y] == 'white':
                windowSurface.blit(whiteImage, rectDst, whiteRect)

# 画出能够落子的位置，无返回值
def drawValidMoves(validmoves):
    for [x,y] in validMoves:
        rectDst = pygame.Rect(BOARDX + x * CELLWIDTH + 2, BOARDY + y * CELLHEIGHT + 2, PIECEWIDTH, PIECEHEIGHT)
        windowSurface.blit(chooseImage, rectDst, chooseRect)

#游戏结束时的界面显示
def drawGameOver(board):
    scorePlayer = getScoreOfBoard(board)[playerTile]
    scoreComputer = getScoreOfBoard(board)[computerTile]
    outputStr = gameoverStr + str(scorePlayer) + ":" + str(scoreComputer)
    text = basicFont.render(outputStr, True, BLACK, BLUE)
    textRect = text.get_rect()
    textRect.centerx = windowSurface.get_rect().centerx
    textRect.centery = windowSurface.get_rect().centery
    windowSurface.blit(text, textRect)

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

chooseImage = pygame.image.load('choose.png')
chooseRect = chooseImage.get_rect()

basicFont = pygame.font.SysFont(None, 36)

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

# 设置窗口界面

windowSurface = pygame.display.set_mode((boardRect.width, boardRect.height))
pygame.display.set_caption('黑白棋')
gameOver = False
# 游戏主循环
validMoves = [[2,4],[3,5],[4,2],[5,3]]

while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            terminate()
        if gameOver == False and turn == 'player' and event.type == MOUSEBUTTONDOWN and event.button == 1:
            x, y = pygame.mouse.get_pos()

            col = int((x - BOARDX) / CELLWIDTH)
            row = int((y - BOARDY) / CELLHEIGHT)

            if makeMove(mainBoard, playerTile, col, row) == True:
                validMoves = getValidMoves(mainBoard, computerTile)
                if validMoves != []:
                    turn = 'computer'
    windowSurface.fill(BACKGROUNDCOLOR)
    windowSurface.blit(boardImage, boardRect, boardRect)

    drawValidMoves(validMoves)
    drawTile(mainBoard)
    # windowSurface.fill(BACKGROUNDCOLOR)
    # windowSurface.blit(boardImage, boardRect, boardRect)

    if isGameOver(mainBoard):
        drawGameOver(mainBoard)

    #刷新显示与计时

    pygame.display.update()
    if isGameOver(mainBoard):
        time.sleep(3)
    mainClock.tick(FPS)

    if (gameOver == False and turn == 'computer'):
        x, y = getComputerMove(mainBoard, computerTile)
        # time.sleep(1)
        makeMove(mainBoard, computerTile, x, y)

        # 玩家有可行的走法
        validMoves = getValidMoves(mainBoard, playerTile)
        if validMoves != []:
            turn = 'player'
