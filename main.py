import pygame
import os
from Dungeon import Game
import neat
import pickle

class DungeonGame:
    def __init__(self, window, width, height):
        self.game = Game(window, width, height)

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
    
    def train_ai(self, genome, config):
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        run = True

        totalMoves = 0
        totalNewMoves = 0
        wins = 0

        while run:
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

            if(self.game.moves > 200 or wins > 6):
                totalMoves += self.game.moves
                totalNewMoves += self.game.newMoves
                self.calculate_fitness(genome, totalMoves, wins, totalNewMoves)
                break
    
    def calculate_fitness(self, genome, totalMoves, wins, newMoves):
        closenessScore = (16 - abs(self.game.playerX - self.game.doorx) + 16 - abs(self.game.playerY - self.game.doory)) * 4
        genome.fitness = wins * 80 + newMoves + closenessScore - totalMoves

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
    game = DungeonGame(window, width, height)
    game.test_game()

def eval_genomes(genomes, config):
    width, height = 640, 640
    window = pygame.display.set_mode((width, height))

    for genome_id, genome in genomes:
            game = DungeonGame(window, width, height)
            game.train_ai(genome, config)


def run_neat(config):
    #p = neat.Population(config)
    p = neat.Checkpointer.restore_checkpoint('neat-checkpoint-98')

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))

    winner = p.run(eval_genomes, 150)
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
    
    test_game()
    #run_neat(config)
    #test_ai(config)