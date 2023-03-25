import pygame
import numpy as np
import random
import time
import copy


class graphics:
    #pygame.init()
    #pygame.font.init()

    #layout for the board constants
    font_size = 24
    cell_size = 100
    offset_canvas = 20
    top_offset = 24
    bottom_spacing = 64

    #colour constants
    black  = (  0,   0,   0)
    white  = (255, 255, 255)
    red    = (255,   0,   0)
    blue   = (  0,   0, 255)
    yellow = (250, 240, 190)
    #def __init__():
        #pass
    def setupDisplay(self, board):
        window_width = 2 * self.offset_canvas + board.width * self.cell_size
        window_height = 2 * self.offset_canvas + self.top_offset + self.bottom_spacing + board.height * self.cell_size
        self.display = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption('Connect Four')
        self.gamefont = pygame.font.Font(None, self.font_size)
        self.display.fill(self.white)
        return(self.display, self.gamefont)
    def drawArrow(self, display, column):
        top_point = (self.offset_canvas + self.cell_size / 2 + self.cell_size * column,
                     self.offset_canvas)
        bottom_point = (self.offset_canvas + self.cell_size / 2 + self.cell_size * column,
                        self.offset_canvas + self.top_offset * 3 / 4)
        left_point = (self.offset_canvas + 3 * self.cell_size / 8 + self.cell_size * column,
                      self.offset_canvas + self.top_offset / 2)
        right_point = (self.offset_canvas + 5 * self.cell_size / 8 + self.cell_size * column,
                       self.offset_canvas + self.top_offset / 2)
        pygame.draw.line(self.display, self.black, left_point, bottom_point, 3)
        pygame.draw.line(self.display, self.black, right_point, bottom_point, 3)
        pygame.draw.line(self.display, self.black, top_point, bottom_point, 3)
    def drawBoard(self, gameDisplay, board, selected_index, red_turn, game_running):
        (display, gamefont) = gameDisplay
        pygame.draw.rect(display, self.white,
                (0, 0, 2 * self.offset_canvas + board.width * self.cell_size,
                2 * self.offset_canvas + self.top_offset + self.bottom_spacing + board.height * self.cell_size),
                0)


        # draw all tokens and circles
        for j in range(board.width):
            for i in range(board.height):
                xc = self.offset_canvas + self.cell_size / 2 + j * self.cell_size
                yc = self.offset_canvas + self.top_offset + self.cell_size / 2 + (board.height - i - 1) * self.cell_size
                if board.field[i][j] == 1:
                    pygame.draw.circle(display, self.red, (int(xc), int(yc)), int(self.cell_size * 2 / 5), 0)
                if board.field[i][j] == 2:
                    pygame.draw.circle(display, self.blue, (int(xc), int(yc)), int(self.cell_size * 2 / 5), 0)
                pygame.draw.circle(display, self.black, (int(xc), int(yc)), int(self.cell_size * 2 / 5), 1)


        # potentially display arrow
        if selected_index >= 0 and game_running and red_turn:
            self.drawArrow(self, display, selected_index)
        # is it the AI player's turn?
        if game_running:
            if red_turn:
                thinking_surf = gamefont.render("Red playing...", False, self.red)
            else:
                thinking_surf = gamefont.render("Blue playing...", False, self.blue)
            display.blit(thinking_surf, (self.offset_canvas + 3 * self.cell_size, 2 * self.offset_canvas + self.top_offset + board.height * self.cell_size))

        pygame.display.update()


    def drawWinners(self, winner):
        if winner == 0:
            wintext = self.gamefont.render("DRAW!", False, self.black)
        elif winner == 1:
            wintext = self.gamefont.render("RED WINS!", False, self.red)
        else:
            wintext = self.gamefont.render("BLUE WINS!", False, self.blue)
        self.display.blit(wintext, (self.offset_canvas, self.offset_canvas / 2))
    def hoveredCol(self, board):
        (mouse_x, mouse_y) = pygame.mouse.get_pos()
        if (mouse_x >= self.offset_canvas \
            and mouse_x < self.offset_canvas + board.width * self.cell_size \
            and mouse_y >= self.offset_canvas + self.top_offset \
            and mouse_y <= self.offset_canvas + self.top_offset + board.height * self.cell_size):
        # The player clicked on a column, not outside
            return int((mouse_x - self.offset_canvas) / self.cell_size)
        else:
        # `-1` is the indicator that nothing has been selected
            return -1


class board:

    #turn tokens
    RED = 1
    BLUE = 2

    board = None
    def __init__(self, h, w):
        self.height = h
        self.width = w
        self.field = [([0] * self.width) for k in range(self.height)]
    def colHeight(self, board, col):
        l = 0
        for index in range(self.height):
            if board[index][col] != 0:
                l += 1
        return l
    def notFullColumns(self):
        cs = []
        for col in range(self.width):
            if self.colHeight(self.field, col) < self.height:
                cs.append(col)
        return cs
    def attemptInsert(self, col, token, engine):
        #checks if a token can be played
        if self.colHeight(self.field, col) < self.height:
            #inserts token in the correct place
            self.field[self.colHeight(self.field, col)][col] = token
            #changes turn
            engine.changeTurn()
            # return True for success
            return True
        else:
            # return False for Failure
            return False
    def isFull(self):
        if self.notFullColumns() == []:
            return True
        else:
            return False


class engine:
    def __init__(self, red_player, blue_player, ai_delay, graphics):
        pygame.init()
        pygame.font.init()

        self.playBoard = board(6,7)
        self.display = graphics.setupDisplay(graphics, self.playBoard)

        self.selectedIndex = -1

        ### PLAYER SETTINGS ###
        self.redPlayer = red_player
        self.bluePlayer = blue_player
        self.aiDelay = ai_delay

        self.gameRunning = True
        self.redTurn = True

    def draw(self, ConnectFourGraphics):
        # A wrapper around the `ConnectFourGraphics.draw_board` function that
        # picks all the right components of `self`.
        ConnectFourGraphics.drawBoard(ConnectFourGraphics, self.display, self.playBoard, self.selectedIndex, self.redTurn, self.gameRunning)

    #gives current player
    def turnToken(self, board):
        if self.redTurn:
            return board.RED
        else:
            return board.BLUE

    def changeTurn(self):
        if self.redTurn:
            self.redTurn = False
        else:
            self.redTurn = True

    def humanTurn(self):
        if self.redTurn and self.redPlayer is None:
            # It's red's turn and red's human
            return True
        elif (not self.redTurn) and self.bluePlayer is None:
            # It's blue's turn and blue's human
            return True
        else:
            return False

    def gameLoop(self, ConnectFourGraphics):
        while self.gameRunning:

            # Let the AI play if it's its turn
            if not self.humanTurn():
                start_ai_time = pygame.time.get_ticks()
                token = self.turnToken(self.playBoard)
                if token == self.playBoard.RED:
                    move = self.redPlayer(copy.deepcopy(self.playBoard.field), self.playBoard, token)
                elif token == self.playBoard.BLUE:
                    move = self.bluePlayer(copy.deepcopy(self.playBoard.field), self.playBoard, token)
                self.playBoard.attemptInsert(move, token, self)
                stop_ai_time = pygame.time.get_ticks()
                ai_time_span = stop_ai_time - start_ai_time
                if ai_time_span < self.aiDelay:
                    pygame.time.delay(self.aiDelay - ai_time_span)

            # Process all events, especially mouse events.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit(0)
                if event.type == pygame.MOUSEMOTION:
                    self.selectedIndex = \
                        ConnectFourGraphics.hoveredCol(ConnectFourGraphics, self.playBoard)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.humanTurn():
                        self.playBoard.attemptInsert(self.selectedIndex, self.turnToken(self.playBoard), self)

            if engine.checkWin(self.playBoard) != None:
                graphics.drawWinners(ConnectFourGraphics, engine.checkWin(self.playBoard))
                self.gameRunning = False
            if self.playBoard.isFull():
                graphics.drawWinners(ConnectFourGraphics, 0)
                self.gameRunning = False

            # Refresh the display and loop back
            self.draw(ConnectFourGraphics)
            pygame.time.wait(40)

        # Once the game is finished, simply wait for the `QUIT` event
        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)
            pygame.time.wait(60)

    #checks all possible winning places to check for a winner
    def checkWin(board):
        winner = None

        #horizontal checks
        for h in range(board.width-3):
            for w in range(board.height):
                if board.field[w][h] != 0:
                    if board.field[w][h] == board.field[w][h+1] == board.field[w][h+2] == board.field[w][h+3]:
                        winner = board.field[w][h]

        #vertical checks
        for v in range(board.width):
            for x in range(board.height - 3):
                if board.field[x][v] != 0:
                    if board.field[x][v] == board.field[x+1][v] == board.field[x+2][v] == board.field[x+3][v]:
                        winner = board.field[x][v]

        #diagonal up left checks
        for l in range(board.width - 3):
            for y in range(board.height - 3):
                if board.field[y][l] != 0:
                    if board.field[y][l] == board.field[y+1][l+1] == board.field[y+2][l+2] == board.field[y+3][l+3]:
                        winner = board.field[y][l]

        #diagonal up right checks
        for r in range(3, board.width):
            for z in range(board.height - 3):
                if board.field[z][r] != 0:
                    if board.field[z][r] == board.field[z+1][r-1] == board.field[z+2][r-2] == board.field[z+3][r-3]:
                        winner = board.field[z][r]
        return winner



class randomAI:
    def playTurn(board, token):
        choices = board.notFullColumns()
        moveCol = choices[random.randint(0, len(choices) - 1)]
        #time.sleep(0.5)
        return(moveCol)


class AI:
    def findWindowScore(window, player):
        score = 0
        oppPlayer = [1,2][player == 1]

        if window.count(player) == 4:
            score += 100
        elif window.count(player) == 3 and window.count(0) == 1:
            score += 20
        elif window.count(player) ==2 and window.count(0) == 2:
            score += 5

        if window.count(oppPlayer) == 4:
            score -= 999999
        elif window.count(oppPlayer) ==3 and window.count(0) == 1:
            score -= 99

        return score

    def scoreBoard(field, player):
        window_length = 4
        score = 0

        #score center column
        centerArray = [row[len(field[0])//2] for row in field]
        countCenter = centerArray.count(player)
        score += 6 * countCenter

        #score horizontal
        for r in range(len(field)):
            #make arrays for the rows
            rowArray = [int(i) for i in list(field[r][:])]
            for c in range(len(field[0])-3):
                #split the rows into windows of four
                window = rowArray[c:c + window_length]
                #score window and add onto total score
                score += AI.findWindowScore(window, player)

        #score vertical
        for c in range(len(field[0])):
            colArray = [row[c] for row in field]
            for r in range(len(field)-3):
                window = colArray[r:r + window_length]
                score += AI.findWindowScore(window, player)

        #score diagonal /
        for r in range(len(field) - 3):
            for c in range(len(field[0]) - 3):
                window = [field[r + i][c + i] for i in range(window_length)]
                score += AI.findWindowScore(window, player)

        #score diagonal \
        for r in range(len(field) - 3):
            for c in range(len(field[0]) - 3):
                window = [field[r + 3 - i][c + i] for i in range(window_length)]
                score += AI.findWindowScore(window, player)


        return score

    def pickMove(field, playBoard, player):
        bestScore = -1000000
        bestCol = -1
        #simulates dropping a token in each column
        for col in playBoard.notFullColumns():
            temp_field = copy.deepcopy(field)
            temp_field[playBoard.colHeight(temp_field, col)][col] = player
            score = AI.scoreBoard(temp_field, player)
            #finds the best score and thus the best column to make the move
            if score > bestScore:
                bestScore, bestCol = score, col

        return bestCol





#print(np.matrix(playBoard.field))
#print(playBoard.colHeight(0))
#print(playBoard.notFullColumns())
#print(engine.checkWin(playBoard))
#print(randomAI.chooseTurn(playBoard))
#boardGraphics = graphics()
#boardGraphics.setupDisplay(playBoard)
#boardGraphics.drawBoard(playBoard)
#boardGraphics.draw_arrow(3)
#playBoard = board(6,7)

connect4Graphics = graphics

connectFour = engine(AI.pickMove, None, 200, connect4Graphics)
connectFour.draw(connect4Graphics)

connectFour.gameLoop(connect4Graphics)
