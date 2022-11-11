import numpy as np
import math
import random

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt


class Tile:
    def __init__(self, position, population = 0, voter_preference = 0, instability = 0, district = -1):
        self.position = position #tuple, 1st element is row, 2nd is column
        self.population = population
        self.voter_preference = voter_preference #partisanship of territory from -1 to 1
        self.instability = instability #likelyhood of tile being moved to new district from 0 to 1
        self.district = district #district tile is assigned to


class Region:
    def __init__(self, dimensions, random_distribution = True, vote_source_points = [], population_source_points = []):
        self.dimensions = dimensions #tuple, 1st element is rows, 2nd is columns

        self.random_distribution = random_distribution #boolean for if population and partisanship distribution are randomly generated or from source points
        
        if self.random_distribution: 
            self.population = dimensions[0] * dimensions[1] * 100 #assign arbitrary max population

        else:
            self.vote_source_points = vote_source_points #source points of maximum partisanship from which voters spread out
            self.population_source_points = population_source_points #source points of densest population from which population spreads out

        self.tiles = [[] for row in range(dimensions[0])] #tiles in region
        self.districts = [[] for col in range(dimensions[1])] #districts in region

    def create_tiles(self): #initialize tiles in region
        for row in range(self.dimensions[0]):
            for column in range(self.dimensions[1]):
                self.tiles[row].append(Tile((row, column)))

    def simulate_agent_movements(self, agent_starting_pos, agents):
        for agent in agents: #simulate movement for every agent
            agent_pos = [agent_starting_pos[0], agent_starting_pos[1]]

            for move in range(agent): #make moves until agent has made maximum number of moves
                while True: #make random moves to adjacent squares, retry if move puts agent in invalid location
                    move = random.choice([(-1, 0), (0, 1), (1, 0), (0, -1)])
                    agent_pos[0] += move[0]
                    agent_pos[1] += move[1]

                    if (0 <= agent_pos[0] and agent_pos[0] < self.dimensions[0]) and (0 <= agent_pos[1] and agent_pos[1] < self.dimensions[1]): #break if agent location is valid
                        break

                    else: #undo previous move if agent move is not valid
                        agent_pos[0] -= move[0]
                        agent_pos[1] -= move[1]

            self.tiles[agent_pos[0]][agent_pos[1]].population += 1 #once agent location is finalized add to tile population

    def assign_tile_populations(self):                
        if self.random_distribution:
            for i in range(3): #create 3 population centers
                agents = [] #each agent contributes 1 to the population
                for agent in range(self.population // 3): #randomly assign each agent a number of moves based on a distribution centered on the amount of moves it takes to reach a corner
                    agents.append(int(np.random.uniform(0, self.dimensions[0] + self.dimensions[1])))

                self.simulate_agent_movements((random.randint(0, self.dimensions[0] - 1),random.randint(0, self.dimensions[1] - 1)), agents) #move each agent to final location

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

    def return_voter_split(self):
        blue_total = 0
        red_total = 0
        for tile_row in self.tiles:
            for tile in tile_row:
                if tile.voter_preference < 0: #if tile blue add it to blue impact
                    blue_total -= tile.voter_preference * tile.population
                    
                else: #else add to red impact
                    red_total += tile.voter_preference * tile.population

        return blue_total * (100 / (blue_total + red_total)), red_total * (100 / (blue_total + red_total)) #convert blue impact and red impact into percentages

    def display_region(self, filter = False, filter_list = []): #if filter is True only display tiles in filter_list
        #create 3d bar graph representing region
        fig = plt.figure()
        ax1 = fig.add_subplot(111, projection = '3d')


        x_pos = np.arange(0, self.dimensions[0], 1)
        y_pos = np.arange(0, self.dimensions[1], 1)
        x_pos, y_pos = np.meshgrid(x_pos, y_pos)
        x_pos = x_pos.flatten()
        y_pos = y_pos.flatten()
        z_pos = [0] * self.dimensions[0] * self.dimensions[1]

        dxy = [1] * self.dimensions[0] * self.dimensions[1] #xy size of each bar
        dz = [] #z height of each bar
        for row in self.tiles:
            for tile in row:
                if tile in filter_list or not filter:
                    dz.append(tile.population)

                else:
                    dz.append(0)

        colors = []
        for row in self.tiles: #assign each bar color based on voter preference
            for tile in row:
                if tile in filter_list or not filter:
                    if tile.voter_preference < 0:
                        colors.append(((1+tile.voter_preference)/1.1, (1+tile.voter_preference)/1.1, 1, 1))

                    else:
                        colors.append((1, (1-tile.voter_preference)/1.16, (1-tile.voter_preference)/1.16, 1))

                else:
                    colors.append((1, 1, 1))

        ax1.bar3d(x_pos, y_pos, z_pos, dxy, dxy, dz, color = colors) #generate graph
        plt.show()
            


if __name__ == '__main__':
    region = Region((20, 20), False, [(5, 5, 1), (17, 14, 1), (6, 12, -1), (16, 6, -1)], [(7, 8, 10000), (3, 7, 8000), (16, 18, 8000), (5, 16, 8000), (14, 3, 8000)]) #initialize randomized 20x20 region
    region.create_tiles() #initialize region tiles
    region.assign_tile_populations() #generate populations
    region.assign_tile_voter_preferences() #generate voter preferences
    print(region.return_voter_split())
    region.display_region()