import numpy as np
import math
import random

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt


class Tile:
    def __init__(self, position, population = 0, voter_preference = 0, instability = 0):
        self.position = position #tuple, 1st element is row, 2nd is column

        self.population = population #population of tile
        self.voter_preference = voter_preference #partisanship of territory from -1 to 1
        self.instability = instability #likelyhood of tile being moved to new district from 0 to 1

class District:
    def __init__(self, tiles, population = 0, voter_preference = 0):
        self.tiles = tiles #tiles in district

        self.population = population #total population of district
        self.voter_preference = voter_preference #combined partisanship of territory from -1 to 1


class Region:
    def __init__(self, dimensions, random_distribution = True, vote_source_points = [], population_source_points = [], max_population_variation = 0.02):
        self.dimensions = dimensions #tuple, 1st element is rows, 2nd is columns

        self.random_distribution = random_distribution #boolean for if population and partisanship distribution are randomly generated or from source points
        
        if self.random_distribution: 
            self.population = dimensions[0] * dimensions[1] * 100 #assign arbitrary max population

        else:
            self.vote_source_points = vote_source_points #source points of maximum partisanship from which voters spread out
            self.population_source_points = population_source_points #source points of densest population from which population spreads out

        self.max_population_variation = max_population_variation #maximum population variation between districts

        self.tiles = [[] for row in range(dimensions[0])] #tiles in region
        self.districts = [[] for col in range(dimensions[1])] #districts in region

    def create_tiles(self): #initialize tiles in region
        for row in range(self.dimensions[0]):
            for column in range(self.dimensions[1]):
                self.tiles[row].append(Tile((row, column)))

    def simulate_agent_movements(self, agent_starting_pos, agents):
        for agent in agents: #simulate movement for every agent
            agent_pos = [agent_starting_pos[0], agent_starting_pos[1]]
            #print(agent_pos)
            for move in range(agent): #make moves until agent has made maximum number of moves
                while True: #make random moves to adjacent squares, retry if move puts agent in invalid location
                    move = random.choice([(-1, 0), (0, 1), (1, 0), (0, -1)])
                    agent_pos[0] += move[0]
                    agent_pos[1] += move[1]

                    if (0 <= agent_pos[0] < self.dimensions[0]) and (0 <= agent_pos[1] < self.dimensions[1]): #break if agent location is valid
                        break

                    else: #undo previous move if agent move is not valid
                        agent_pos[0] -= move[0]
                        agent_pos[1] -= move[1]

            self.tiles[agent_pos[0]][agent_pos[1]].population += 1 #once agent location is finalized add to tile population


    def assign_tile_populations(self):                
        if self.random_distribution:
            agents = [] #each agent contributes 1 to the population
            for agent in range(self.population): #randomly assign each agent a number of moves based on a distribution centered on the amount of moves it takes to reach a corner
                agents.append(int(np.random.uniform(0, self.dimensions[0] + self.dimensions[1])))

            self.simulate_agent_movements((self.dimensions[0] // 2, self.dimensions[1] // 2), agents) #move each agent to final location

        else:
            for source_point in self.population_source_points: #for each source pointcreate agent and do distribution
                agents = []
                for agent in range(source_point[2]):
                    agents.append(int(np.random.uniform(0, self.dimensions[0] + self.dimensions[1])))

                self.simulate_agent_movements((source_point[0], source_point[1]), agents) #move each agent to final location
                

    def calculate_voter_preference(self, position, vote_source_points):
        voter_preference = 0
        for source_point in vote_source_points:
            voter_preference += source_point[2] / max(1, math.sqrt((position[0] - source_point[0]) ** 2 + (position[1] - source_point[1]) ** 2)) #add effect from source point based on power law

        if voter_preference < 0: #ensure voter preference is between -1 and 1
            voter_preference = max(-1, voter_preference)

        else:
            voter_preference = min(1, voter_preference)

        return round(voter_preference, 2)


    def assign_tile_voter_preferences(self):
        if self.random_distribution: #if source points need to be generated
            while True:
                self.vote_source_points = [(random.randint(0, self.dimensions[0] - 1), random.randint(0, self.dimensions[1] - 1), -1 + 2 * (i % 2)) for i in range(max(2, self.dimensions[0] * self.dimensions[1] // 20))] #create source point every 20 tiles alternating between blue and red

                if len(set(self.vote_source_points)) == len(self.vote_source_points): #check for duplicates
                    break

        for row in self.tiles:
            for tile in row:
                tile.voter_preference = self.calculate_voter_preference(tile.position, self.vote_source_points) #get each tile's preference from source point
                
            


if __name__ == '__main__':
    region = Region((20, 20), True) #initialize randomized 20x20 region
    region.create_tiles() #initialize region tiles
    region.assign_tile_populations() #generate populations
    region.assign_tile_voter_preferences() #generate voter preferences

    #create 3d bar graph representing region
    fig = plt.figure()
    ax1 = fig.add_subplot(111, projection = '3d')

    x_pos = [i for i in range(region.dimensions[0]) for j in range(region.dimensions[0])] #xyz of each bar
    y_pos = [i for i in range(region.dimensions[1])] * region.dimensions[1]
    z_pos = [0] * region.dimensions[0] * region.dimensions[1]

    dxy = [1] * region.dimensions[0] * region.dimensions[1] #xy size of each bar
    dz = [region.tiles[i][j].population for i in range(region.dimensions[0]) for j in range(region.dimensions[1])] #z height of each bar

    colors = []
    for row in region.tiles: #assign each bar color based on voter preference
        for tile in row:
            if tile.voter_preference < 0:
                colors.append(((1+tile.voter_preference)/1.16, (1+tile.voter_preference)/1.16, 1, 1))

            else:
                colors.append((1, (1-tile.voter_preference)/1.16, (1-tile.voter_preference)/1.16, 1))

    ax1.bar3d(x_pos, y_pos, z_pos, dxy, dxy, dz, color = colors) 
    plt.show() #display graph


