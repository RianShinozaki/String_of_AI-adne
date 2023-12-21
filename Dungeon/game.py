import pygame
import random

pygame.init()

# 9 - player
# 8 - wall
# 7 - unmapped
# 6 - footsteps
# 2 - door

class GameInformation:
    def __init__(self, moves, gameState):
        self.moves = moves
        self.gameState = gameState

class Game:
    MAPLENGTH = 16
    CELLSIZE = 32
    BLACK = (0, 0, 0)
    RED = (255, 0, 0)
    GAME_FONT = pygame.font.SysFont("comicsans", 50)

    doorx = 1
    doory = 14

    def lookFor(self, x, y, type):
        return (self.map[x][y] == type)

    def generate_maze(self):
        
        random.seed(406)

        #Populate the maze with breakable walls        
        self.map = [[7 for x in range(self.MAPLENGTH)] for y in range(self.MAPLENGTH)]

        #Make the boundaries
        for x in range(self.MAPLENGTH):
            for y in range(self.MAPLENGTH):
                if(x == 0 or x == self.MAPLENGTH-1):
                    self.map[x][y] = 8
                if(y == 0 or y == self.MAPLENGTH-1):
                    self.map[x][y] = 8

        posX = 1
        posY = 14
        holes = 0
        dirs = [[1, 0],[0, 1], [-1, 0],[0, -1]]
        tunneling = True

        backtrackfailsafe = 0
        backtrackfailsafeMax = 25

        self.doorx = 1
        self.doory = 14

        self.map[posX][posY] = 5
        
        #Tunnel randomly through the maze, creating walls and backtracking if necessary
        while tunneling:
            rots = 0
            dir = random.randint(0, 3)
            searching = True
            while searching:
                theDir = dirs[dir]
                if(self.lookFor(posX + theDir[0], posY + theDir[1], 7)):
                    
                    if(self.lookFor(posX + theDir[1], posY + theDir[0], 7)):
                        self.map[posX + theDir[1]][posY + theDir[0]] = 8
                    if(self.lookFor(posX - theDir[1], posY - theDir[0], 7)):
                        self.map[posX - theDir[1]][posY - theDir[0]] = 8
                    
                    posX += theDir[0]
                    posY += theDir[1]

                    self.map[posX][posY] = dir

                    searching = False
                    holes += 1
                    backtrackfailsafe = 0
                    if(posX > 10 or posY < 6):
                        self.doorx = posX
                        self.doory = posY

                    if(holes > 120):
                        tunneling = False
                
                dir = (dir + 1) % 4
                rots += 1

                #Nowhere left to go, so backtrack one step
                if(rots > 4):
                    backtrackfailsafe += 1
                    if(backtrackfailsafe < backtrackfailsafeMax):
                        searching = False
                        returnDir = self.map[posX][posY]
                        if(returnDir > 3):
                            tunneling = False
                        else:  
                            posX -= dirs[returnDir][0]
                            posY -= dirs[returnDir][1]
                    else:
                        tunneling = False
                        searching = False

        #Create spacious starting area

        self.map[1][14] = 0
        self.map[2][14] = 0
        self.map[3][14] = 0
        self.map[1][13] = 0
        self.map[2][13] = 0
        self.map[3][13] = 0
        self.map[1][12] = 0
        self.map[2][12] = 0
        self.map[3][12] = 0

        # "Smooth over" map
        for x in range(self.MAPLENGTH):
            for y in range(self.MAPLENGTH):
                if(self.map[x][y] < 4):
                    self.map[x][y] = 0
                if(self.map[x][y] == 7):
                    self.map[x][y] = 8

        self.map[2][13] = 9
        
        #Make sure the door is placed properly
        addDoor = (self.doorx == 1 and self.doory == 14)
        if(not addDoor):
           self.map[self.doorx][self.doory] = 2

        while(addDoor):
            self.doorx = random.randint(1, 14)
            self.doory = random.randint(1, 14)
            if(self.map[self.doorx][self.doory] == 0):
                self.map[self.doorx][self.doory] = 2
                addDoor = False
        

    def __init__(self, window, window_width, window_height, darkness = 200):
        self.window_width = window_width
        self.window_height = window_height
        self.window = window
        self.gameState = 0

        self.generate_maze()

        self.playerX = 2
        self.playerY = 13

        self.map[self.playerX][self.playerY] = 9

        self.moves = 0
        self.okayMoves = 0
        self.newMoves = 0

        self.PLAYERIMAGE = pygame.image.load("Dungeon/Theseus.png").convert()
        self.PLAYERIMAGE = pygame.transform.scale(self.PLAYERIMAGE, (32, 32))

        self.WALLIMAGE = pygame.image.load("Dungeon/Wall.png").convert()
        self.WALLIMAGE = pygame.transform.scale(self.WALLIMAGE, (32, 32))

        self.FLOORIMAGE = pygame.image.load("Dungeon/Floor.png").convert()
        self.FLOORIMAGE = pygame.transform.scale(self.FLOORIMAGE, (32, 32))

        self.DOORIMAGE = pygame.image.load("Dungeon/Door.png").convert()
        self.DOORIMAGE = pygame.transform.scale(self.DOORIMAGE, (32, 32))

        self.FOOTSTEPIMAGE = pygame.image.load("Dungeon/Footsteps.png").convert()
        self.FOOTSTEPIMAGE = pygame.transform.scale(self.FOOTSTEPIMAGE, (32, 32))

        self.DARKNESSIMAGE = pygame.image.load("Dungeon/Darkness.png").convert_alpha()
        self.DARKNESSIMAGE = pygame.transform.scale(self.DARKNESSIMAGE, (640*2, 640*2))
        self.DARKNESSIMAGE.set_alpha(darkness)

    def draw(self):
        if(self.gameState == 0):
            self.window.fill(self.BLACK)
            for x in range(self.MAPLENGTH):
                for y in range(self.MAPLENGTH):
                    if(self.map[x][y] == 9):
                        self.window.blit(self.PLAYERIMAGE, (x* self.CELLSIZE, y* self.CELLSIZE) )
                    elif(self.map[x][y] == 8):
                        self.window.blit(self.WALLIMAGE, (x* self.CELLSIZE, y* self.CELLSIZE) )
                    elif(self.map[x][y] == 7):
                        self.window.blit(self.WALLIMAGE, (x* self.CELLSIZE, y* self.CELLSIZE) )
                    elif(self.map[x][y] == 6):
                        self.window.blit(self.FOOTSTEPIMAGE, (x* self.CELLSIZE, y* self.CELLSIZE) )
                    else:
                        self.window.blit(self.FLOORIMAGE, (x* self.CELLSIZE, y* self.CELLSIZE) )

                    #num = self.GAME_FONT.render(f"{self.map[x][y]}", 1, self.RED)
                    #num = pygame.transform.scale(num, (16, 16))
                    #self.window.blit(num, (x * self.CELLSIZE, y * self.CELLSIZE))
                    #elif(self.map[x][y] == 5):
                        #self.window.blit(self.DOORIMAGE, (x* self.CELLSIZE, y* self.CELLSIZE) )
            
            self.window.blit(self.DARKNESSIMAGE, (self.playerX * self.CELLSIZE - 640, self.playerY * self.CELLSIZE - 640 + 32) )
            self.window.blit(self.DOORIMAGE, (self.doorx* self.CELLSIZE, self.doory* self.CELLSIZE) )

            moves_score = self.GAME_FONT.render("MOVES: " + f"{self.okayMoves}", 1, self.RED)
            self.window.blit(moves_score, (self.MAPLENGTH * self.CELLSIZE / 2, self.MAPLENGTH * self.CELLSIZE))
        if(self.gameState == 1):
            self.window.fill(self.BLACK)
            moves_score = self.GAME_FONT.render("YOU WIN", 1, self.RED)
            self.window.blit(moves_score, (0, self.MAPLENGTH * self.CELLSIZE / 2))

            moves_score = self.GAME_FONT.render("Press Enter to retry", 1, self.RED)
            self.window.blit(moves_score, (0, self.MAPLENGTH * self.CELLSIZE / 2 + 48))

    def move_player(self, x, y):
        self.moves += 1
        if(self.map[self.playerX + x][self.playerY + y] != 8):
            self.map[self.playerX][self.playerY] = 6
            self.playerX += x
            self.playerY += y
            self.okayMoves += 1
            if(self.map[self.playerX][self.playerY] == 0):
                self.newMoves += 1

            if(self.map[self.playerX][self.playerY] == 2):
                self.gameState = 1

            self.map[self.playerX][self.playerY] = 9    
            return True   

        return False

    def get_inputs(self):
        wall_left1 = self.map[self.playerX - 1][self.playerY]
        wall_right1 = self.map[self.playerX + 1][self.playerY]
        wall_down1 = self.map[self.playerX][self.playerY + 1]
        wall_up1 = self.map[self.playerX][self.playerY - 1]

        wall_upleft = self.map[self.playerX - 1][self.playerY - 1]
        wall_upright = self.map[self.playerX + 1][self.playerY - 1]
        wall_downleft = self.map[self.playerX - 1][self.playerY + 1]
        wall_downright = self.map[self.playerX + 1][self.playerY + 1]

        try:
            wall_left2 = self.map[self.playerX - 2][self.playerY]
        except:
            wall_left2 = 8
        
        try:
            wall_right2 = self.map[self.playerX + 2][self.playerY]
        except:
            wall_right2 = 8
        
        try:
            wall_down2 = self.map[self.playerX][self.playerY + 2]
        except:
            wall_down2 = 8
        
        try:
            wall_up2 = self.map[self.playerX][self.playerY - 2]
        except:
            wall_up2 = 8

        #print("wall_left1 ", wall_left1)
        #print("wall_left2 ", wall_left2)
        #print("wall_right1 ", wall_right1)
        #print("wall_right2 ", wall_right2)
        #print("wall_up1 ", wall_up1)
        #print("wall_up2 ", wall_up2)
        #print("wall_down1 ", wall_down1)
        #print("wall_down2 ", wall_down2)

        #return (wall_left1, wall_right1, wall_down1, wall_up1, self.playerX, self.playerY, self.doorx, self.doory)
        #return (wall_left1, wall_right1, wall_down1, wall_up1, wall_upleft, wall_upright, wall_downleft, wall_downright, wall_left2, wall_right2, wall_down2, wall_up2, self.playerX, self.playerY, self.doorx, self.doory, self.doorx - self.playerX, self.doory - self.playerY)
        return (wall_left1, wall_right1, wall_down1, wall_up1, wall_upleft, wall_upright, wall_downleft, wall_downright, wall_left2, wall_right2, wall_down2, wall_up2, self.playerX, self.playerY, self.doorx, self.doory)
        #return (wall_left1, wall_right1, wall_down1, wall_up1, wall_upleft, wall_upright, wall_downleft, wall_downright, wall_left2, wall_right2, wall_down2, wall_up2, self.doorx - self.playerX, self.doory - self.playerY)

    def restart(self):
        self.playerX = 2
        self.playerY = 13
        self.moves = 0
        self.gameState = 0
        self.newMoves = 0
        self.okayMoves = 0
        self.generate_maze()
    
        
