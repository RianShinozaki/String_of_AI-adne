import pygame
import os
from Dungeon import Game
import neat
import pickle

class DungeonGame:
    def __init__(self, window, width, height, darkness = 200):
        self.game = Game(window, width, height, darkness)

    def test_game(self):
        run = True
        clock = pygame.time.Clock()
        while run:
            clock.tick(10)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                    break
            
            keys = pygame.key.get_pressed()
            if(self.game.gameState == 0):
                if keys[pygame.K_UP]:
                    self.game.move_player(0, -1)
                if keys[pygame.K_DOWN]:
                    self.game.move_player(0, 1)
                if keys[pygame.K_RIGHT]:
                    self.game.move_player(1, 0)
                if keys[pygame.K_LEFT]:
                    self.game.move_player(-1, 0)

            if keys[pygame.K_RETURN] and self.game.gameState == 1:
                self.game.restart()

            self.game.get_inputs()
            self.game.draw()
            pygame.display.update()
    
    def train_ai(self, genome, config, draw):
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        run = True

        totalMoves = 0
        totalOkayMoves = 0
        totalNewMoves = 0
        lastNewMoves = 0
        stepScore = 0
        wins = 0

        clock = pygame.time.Clock()

        while run:
            #clock.tick(30)

            giveUp = False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
            
            output = net.activate( self.game.get_inputs() )
            decision = output.index(max(output))

            decRes = False
            if decision == 0:
                decRes = self.game.move_player(1, 0)
            if decision == 1:
                decRes = self.game.move_player(0, 1)
            if decision == 2:
                decRes = self.game.move_player(-1, 0)
            if decision == 3:
                decRes = self.game.move_player(0, -1)
            
            if(decRes == False):
                giveUp = True

            if(self.game.newMoves > lastNewMoves):
                closenessScore = (8 - abs(self.game.playerX - self.game.doorx) + 8 - abs(self.game.playerY - self.game.doory)) 
                stepScore += closenessScore
                lastNewMoves = self.game.newMoves

            if(draw):
                self.game.draw()
                pygame.display.update()

            if(self.game.gameState == 1):
                totalOkayMoves += self.game.okayMoves
                totalNewMoves += self.game.newMoves
                wins += 1
                self.game.restart()
                lastNewMoves = 0

            if(self.game.moves > 200 or wins > 6):
                giveUp = True

            if(giveUp):
                totalMoves += self.game.moves
                totalNewMoves += self.game.newMoves
                self.calculate_fitness(genome, wins, stepScore)
                break
    
    def calculate_fitness(self, genome, wins, stepScore):
        genome.fitness = wins * 80 + stepScore * 0.4 

    def test_ai(self, genome, config):
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        run = True

        totalMoves = 0
        totalNewMoves = 0
        wins = 0

        clock = pygame.time.Clock()

        while run:
            clock.tick(10)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
            
            output = net.activate( self.game.get_inputs() )
            decision = output.index(max(output))
            if decision == 0:
                self.game.move_player(1, 0)
            if decision == 1:
                self.game.move_player(0, 1)
            if decision == 2:
                self.game.move_player(-1, 0)
            if decision == 3:
                self.game.move_player(0, -1)
            
            self.game.draw()
            pygame.display.update()

            if(self.game.gameState == 1):
                totalMoves += self.game.moves
                totalNewMoves += self.game.newMoves
                wins += 1
                self.game.restart()

    


def test_game():
    width, height = 640, 640
    window = pygame.display.set_mode((width, height))
    game = DungeonGame(window, width, height, darkness = 256)
    game.test_game()

def eval_genomes(genomes, config):
    width, height = 640, 640
    window = pygame.display.set_mode((width, height))

    for genome_id, genome in genomes:
            game = DungeonGame(window, width, height)
            game.train_ai(genome, config, True)


def run_neat(config, draw):
    p = neat.Population(config)
    p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-77')

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))

    winner = p.run(eval_genomes, 500)
    with open("best.pickle", "wb") as f:
        pickle.dump(winner, f)
    
def test_ai(config):
    width, height = 640, 640
    window = pygame.display.set_mode((width, height))

    with open("best.pickle", "rb") as f:
        winner = pickle.load(f)

    game = DungeonGame(window, width, height)
    game.test_ai(winner, config)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")

    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)
    
    #test_game()
    #run_neat(config, True)
    test_ai(config)