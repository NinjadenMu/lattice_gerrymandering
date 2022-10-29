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

    def score_district(self, num_districts, edge_tiles, first_eval = True, pop_deltas = []):
        if first_eval:
            self.populations = [0 for district in range(num_districts)]

            for row in self.region.tiles:
                for tile in row:
                    self.populations[tile.district] += tile.population

            district_perimeters_to_area = [0 for district in range(len(self.districts))]
            for district in range(len(self.districts)):
                for edge_tile in edge_tiles:
                    if edge_tile[0].district == district:
                        district_perimeters_to_area[district] += 1

                district_perimeters_to_area[district] /= len(self.districts[district])


        std_dev = sum([(sum(self.populations) / len(self.populations) - pop) ** 2 for pop in self.populations]) ** 0.5
        
        district_voter_preferences = [0 for district in range(num_districts)]
        for district in range(num_districts):
            for tile in self.districts[district]:
                district_voter_preferences[district] += tile.voter_preference

            if district_voter_preferences[district] < 0:
                district_voter_preferences[district] = -1

            elif district_voter_preferences[district] > 0:
                district_voter_preferences[district] = 1

        return std_dev + 300 * sum(district_perimeters_to_area) / len(district_perimeters_to_area) + 10000 * sum(district_voter_preferences)

    def get_edge_tiles(self, first_pass = True, flipped_tile = None, prev_edge_tiles = []):
        if first_pass:        
            edge_tiles = []
            for row in self.region.tiles:
                for tile in row:
                    edge_tile_data = []
                    if (tile.position[0] + 1) < region.dimensions[0] and (tile.position[1]) < region.dimensions[1] and self.region.tiles[tile.position[0] + 1][tile.position[1]].district != tile.district:
                        edge_tile_data.append(self.region.tiles[tile.position[0] + 1][tile.position[1]].district)

                    if (tile.position[0] - 1) >= 0 and (tile.position[1]) >= 0 and self.region.tiles[tile.position[0] - 1][tile.position[1]].district != tile.district:
                        edge_tile_data.append(self.region.tiles[tile.position[0] - 1][tile.position[1]].district)

                    if (tile.position[0]) >= 0 and (tile.position[1] + 1) < region.dimensions[1] and self.region.tiles[tile.position[0]][tile.position[1] + 1].district != tile.district:
                        edge_tile_data.append(self.region.tiles[tile.position[0]][tile.position[1] + 1].district)

                    if (tile.position[0]) < region.dimensions[0] and (tile.position[1] - 1) >= 0 and self.region.tiles[tile.position[0]][tile.position[1] - 1].district != tile.district:
                        edge_tile_data.append(self.region.tiles[tile.position[0]][tile.position[1] - 1].district)

                    if edge_tile_data != []:
                        edge_tile_data.insert(0, tile)
                        edge_tiles.append(edge_tile_data)

        else:
            neighbours = [flipped_tile]
            for edge in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                if flipped_tile.position[0] + edge[0] >= 0 and flipped_tile.position[0] + edge[0] < self.region.dimensions[0] and flipped_tile.position[1] + edge[1] >=0 and flipped_tile.position[1] + edge[1] < self.region.dimensions[1]:
                    neighbours.append(self.region.tiles[flipped_tile.position[0] + edge[0]][flipped_tile.position[1] + edge[1]])

            i = 0
            while i < len(prev_edge_tiles):
                tile_on = prev_edge_tiles[i][0]
                if tile_on in neighbours:
                    prev_edge_tiles.pop(i)
                    i -= 1

                i += 1

            for tile in neighbours:
                edge_tile_data = []
                if (tile.position[0] + 1) < region.dimensions[0] and (tile.position[1]) < region.dimensions[1] and self.region.tiles[tile.position[0] + 1][tile.position[1]].district != tile.district:
                    edge_tile_data.append(self.region.tiles[tile.position[0] + 1][tile.position[1]].district)

                if (tile.position[0] - 1) >= 0 and (tile.position[1]) >= 0 and self.region.tiles[tile.position[0] - 1][tile.position[1]].district != tile.district:
                    edge_tile_data.append(self.region.tiles[tile.position[0] - 1][tile.position[1]].district)

                if (tile.position[0]) >= 0 and (tile.position[1] + 1) < region.dimensions[1] and self.region.tiles[tile.position[0]][tile.position[1] + 1].district != tile.district:
                    edge_tile_data.append(self.region.tiles[tile.position[0]][tile.position[1] + 1].district)

                if (tile.position[0]) < region.dimensions[0] and (tile.position[1] - 1) >= 0 and self.region.tiles[tile.position[0]][tile.position[1] - 1].district != tile.district:
                    edge_tile_data.append(self.region.tiles[tile.position[0]][tile.position[1] - 1].district)

                if edge_tile_data != []:
                    edge_tile_data.insert(0, tile)
                    prev_edge_tiles.append(edge_tile_data)   

            edge_tiles = prev_edge_tiles       

        return edge_tiles

    def dfs(self, visited, node_on, district):
        if len(visited) >= len(district):
            return True

        edges = [(1, 0), (0, 1), (-1, 0), (0, -1)]

        for edge in edges:
            if node_on.position[0] + edge[0] >= 0 and node_on.position[0] + edge[0] < self.region.dimensions[0] and node_on.position[1] + edge[1] >=0 and node_on.position[1] + edge[1] < self.region.dimensions[1]:
                if self.region.tiles[node_on.position[0] + edge[0]][node_on.position[1] + edge[1]].district == node_on.district and self.region.tiles[node_on.position[0] + edge[0]][node_on.position[1] + edge[1]] not in visited:
                    visited.append(self.region.tiles[node_on.position[0] + edge[0]][node_on.position[1] + edge[1]])    
                    if self.dfs(visited, self.region.tiles[node_on.position[0] + edge[0]][node_on.position[1] + edge[1]], district):
                        return True
        #self.region.display_region(True, visited)
        return False

    def check_if_continuous(self, district):
        return self.dfs([district[0]], district[0], district)

    def mcmc(self, num_districts):
        start = time.perf_counter()
        self.voronoi_districts(num_districts)

        for i in range(5000):
            if i == 0:
                edge_tiles = self.get_edge_tiles(True)

            elif use_from_eval:
                edge_tiles = eval_edge_tiles
                use_from_eval = False

            else: 
                edge_tiles = self.get_edge_tiles(False, tile_to_flip[0], edge_tiles)

            tile_to_flip = random.choices(edge_tiles, weights = [len(edge_tile) for edge_tile in edge_tiles], k = 1)[0]

            original_score = self.score_district(num_districts, edge_tiles)
            if i == 0:
                print(original_score)

            original_district = tile_to_flip[0].district

            tile_to_flip[0].district = random.choice(tile_to_flip[1:])
            self.districts[original_district].remove(tile_to_flip[0])
            if self.check_if_continuous(self.districts[original_district]):
                use_from_eval = True
                self.districts[tile_to_flip[0].district].append(tile_to_flip[0])
                eval_edge_tiles = self.get_edge_tiles(False, tile_to_flip[0], edge_tiles)
                new_score = self.score_district(num_districts, eval_edge_tiles)
                #print(original_score, new_score)
                if original_score < new_score and random.random() >= 0:
                    self.districts[original_district].append(tile_to_flip[0])
                    self.districts[tile_to_flip[0].district].remove(tile_to_flip[0])
                    tile_to_flip[0].district = original_district
                    use_from_eval = False

            else:
                tile_to_flip[0].district = original_district
                self.districts[original_district].append(tile_to_flip[0])
        
        print(self.score_district(num_districts, edge_tiles))
        print(time.perf_counter() - start)
        total_pop = 0
        districts = [[] for district in range(num_districts)]
        for row in self.region.tiles:
            for tile in row:
                total_pop += tile.population

        print(total_pop)

        district_voter_preferences = [0 for district in range(num_districts)]
        for district in range(num_districts):
            for tile in self.districts[district]:
                district_voter_preferences[district] += tile.voter_preference

        print(district_voter_preferences)

        self.region.display_region()
        for district in self.districts:
            #print(1)
            print(self.check_if_continuous(district))
            self.region.display_region(True, district)
    




        


gerrymander = Gerrymander(region, 'red')
gerrymander.mcmc(6)