from region import *
import random
import math
import time

region = Region((20, 20), False, [(5, 5, 1), (17, 14, 1), (6, 12, -1), (16, 6, -1)], [(7, 8, 10000), (3, 7, 8000), (16, 18, 8000), (5, 16, 8000), (14, 3, 8000)])
region.create_tiles()
region.assign_tile_populations()
region.assign_tile_voter_preferences()

class Gerrymander:
    def __init__(self, region, party):
        self.region = region
        self.party = party

    def voronoi_districts(self, num_districts):
        district_centers = []

        for district in range(num_districts):
            while 1:
                tile = random.choice(random.choice(self.region.tiles))

                if tile.district == -1:
                    tile.district = district
                    district_centers.append(tile.position)
                    break

        for row in self.region.tiles:
            for tile in row:
                distances = []
                if tile.district == -1:
                    for district_center in district_centers:
                        distances.append(((district_center[0] - tile.position[0]) ** 2 + (district_center[1] - tile.position[1]) ** 2) ** 0.5)

                    tile.district = distances.index(min(distances))
            
        districts = [[] for district in range(num_districts)]
        for row in self.region.tiles:
            for tile in row:
                districts[tile.district].append(tile)

        self.districts = districts

        #self.region.display_region()
        #for district in districts:
            #self.region.display_region(True, district)


    def score_district(self, num_districts, first_eval = True, pop_deltas = []):
        if first_eval:
            self.populations = [0 for district in range(num_districts)]

            for row in self.region.tiles:
                for tile in row:
                    self.populations[tile.district] += tile.population

        else:
            for i, delta in enumerate(pop_deltas):
                self.populations[i] += delta

        total_deviation = 0
        average = sum(self.populations) / num_districts
        for population in self.populations:
            total_deviation += (population - average) ** 2

        std_dev = math.sqrt(total_deviation)

        if first_eval:
            pass

        else:
            for i, delta in enumerate(pop_deltas):
                self.populations[i] -= delta

        return std_dev

    def get_edge_tiles(self,first_pass = True):
        if first_pass:        
            edge_tiles = []
            for row in self.region.tiles:
                for tile in row:
                    edge_tile_data = []
                    if (tile.position[0] + 1) < region.dimensions[0] and (tile.position[1] + 1) < region.dimensions[1] and self.region.tiles[tile.position[0] + 1][tile.position[1] + 1].district != tile.district:
                        edge_tile_data.append(self.region.tiles[tile.position[0] + 1][tile.position[1] + 1].district)

                    if (tile.position[0] - 1) >= 0 and (tile.position[1] - 1) >= 0 and self.region.tiles[tile.position[0] - 1][tile.position[1] - 1].district != tile.district:
                        edge_tile_data.append(self.region.tiles[tile.position[0] - 1][tile.position[1] - 1].district)

                    if (tile.position[0] - 1) >= 0 and (tile.position[1] + 1) < region.dimensions[1] and self.region.tiles[tile.position[0] - 1][tile.position[1] + 1].district != tile.district:
                        edge_tile_data.append(self.region.tiles[tile.position[0] - 1][tile.position[1] + 1].district)

                    if (tile.position[0] + 1) < region.dimensions[0] and (tile.position[1] - 1) >= 0 and self.region.tiles[tile.position[0] + 1][tile.position[1] - 1].district != tile.district:
                        edge_tile_data.append(self.region.tiles[tile.position[0] + 1][tile.position[1] - 1].district)

                    if edge_tile_data != []:
                        edge_tile_data.insert(0, tile)
                        edge_tiles.append(edge_tile_data)

        #lse:

        return edge_tiles

    def dfs(self, visited, node_on, district):
        if len(visited) == len(district) - 1:
            return True

        edges = [(1, 1), (1, -1), (-1, 1), (-1, -1)]

        for edge in edges:
            

    def check_if_continuous(self, district):


    def mcmc(self, num_districts):
        total_time = 0
        self.voronoi_districts(num_districts)
        print(self.score_district(num_districts))

        for i in range(1000):
            original_score = self.score_district(num_districts)
            start = time.perf_counter()
            tile_to_flip = random.choice(self.get_edge_tiles(True))
            stop = time.perf_counter()
            total_time += stop - start
            original_district = tile_to_flip[0].district

            tile_to_flip[0].district = random.choice(tile_to_flip[1:])
            self.districts[original_district].remove(tile_to_flip[0])
            self.districts[tile_to_flip[0].district].append(tile_to_flip[0])

            new_score = self.score_district(num_districts)

            if original_score < new_score and random.random() > 0.4:
                self.districts[original_district].append(tile_to_flip[0])
                self.districts[tile_to_flip[0].district].remove(tile_to_flip[0])
                tile_to_flip[0].district = original_district
        
        print(self.score_district(num_districts))
        print(total_time)
        districts = [[] for district in range(num_districts)]
        for row in self.region.tiles:
            for tile in row:
                districts[tile.district].append(tile)

        self.region.display_region()
        for district in districts:
            self.region.display_region(True, district)
    




        


gerrymander = Gerrymander(region, 'red')
gerrymander.mcmc(5)