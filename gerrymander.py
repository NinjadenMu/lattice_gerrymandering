from region import *
import random
import math
import time
import copy

region = Region((19, 19), False, [(5, 5, 1), (17, 14, 1), (6, 12, -1), (16, 6, -1)], [(7, 8, 10000), (3, 7, 8000), (16, 18, 8000), (5, 16, 8000), (14, 3, 8000)])
region.create_tiles()
region.assign_tile_populations()
region.assign_tile_voter_preferences()
"""
for row in region.tiles: #give all tiles equal populations - only good for visual purposes
    for tile in row:
        tile.population = 10
"""
class Gerrymander:
    def __init__(self, region, party, num_districts, curve):
        self.region = region
        self.party = party #party to favor, overall + (red) or - (blue)
        self.curve_sorted = False
        self.num_districts = num_districts
        self.curve = curve #target voter preference for each district

    def voronoi_districts(self): #generate initial districts with voronoi tesselation
        district_centers = []
        self.districts = [[] for district in range(self.num_districts)]

        for district in range(self.num_districts): #randomly choose centers of districts
            while 1:
                tile = random.choice(random.choice(self.region.tiles))

                if tile.district == -1:
                    tile.district = district
                    district_centers.append(tile.position)
                    self.districts[tile.district].append(tile)
                    break

        for row in self.region.tiles: #calculate distance from each tile to all centers, assign to district of center tile is closest to
            for tile in row:
                distances = []
                if tile.district == -1: #if tile is not a center tile
                    for district_center in district_centers:
                        distances.append(((district_center[0] - tile.position[0]) ** 2 + (district_center[1] - tile.position[1]) ** 2) ** 0.5)

                    tile.district = distances.index(min(distances))
                    self.districts[tile.district].append(tile)


    #def generate_curve(self):
       # self.curve = [0.05, 0.05, 0.05, 0.05, 0.05, -0.3]
    #Add code to auto generate target district voter preference

    def sort_list(self, list1, list2): #rearrange order of curve so that each target district voter preference is closest to actual voter preferences of initial districts
        new_list1 = [0 for i in range(len(list1))] #new target district voter preferences curve

        list1 = sorted(list1) #sort current target curve
        keyed_list2 = sorted([(list2[i], i) for i in range(len(list2))], key = lambda x: x[0]) #sort actual voter preferences, but each value becomes a tuple (voter preference, value's original index).  
        #since both actual and target voter preferences are sorted, the actual and target voter preferences are arranged so that each value is closest to its corresponding value

        #to reorder the target voter curve, since actual voter preferences is not being rearranged, we move each target value to the index of its corresponding actual value
        for i, pair in enumerate(keyed_list2):
            new_list1[pair[1]] = list1[i]

        return new_list1

    #def compactness(self):
        #pass
    #add code to help eval function ensure districts are comapct and uniformly shaped

    def score_district(self, edge_tiles, first_eval = True, pop_deltas = []): #fitness function for districts, smaller num = better
        if first_eval: #if first iteration, do naive full evaluation
            self.populations = [0 for district in range(self.num_districts)]

            for row in self.region.tiles:
                for tile in row:
                    self.populations[tile.district] += tile.population

            district_perimeters_to_area = [0 for district in range(len(self.districts))]
            for district in range(len(self.districts)):
                for edge_tile in edge_tiles:
                    if edge_tile[0].district == district:
                        district_perimeters_to_area[district] += 1

                district_perimeters_to_area[district] /= len(self.districts[district])


            std_dev = sum([(sum(self.populations) / len(self.populations) - pop) ** 2 for pop in self.populations]) ** 0.5 #calculate std deviation of pop between districts, want districts to have similar pops
            
            district_voter_preferences = [0 for district in range(self.num_districts)]
            for district in range(self.num_districts): # calcualte actual district voter preference curve
                for tile in self.districts[district]:
                    district_voter_preferences[district] += tile.voter_preference * tile.population

                district_voter_preferences[district] /= self.populations[district]
        
        if not self.curve_sorted: #if curve has not been sorted to match actual preferences, sort but do not do this again
            self.curve = self.sort_list(self.curve, district_voter_preferences)
            print(self.curve, district_voter_preferences)
            self.curve_sorted = True

        return 2* std_dev + 60000 * sum([(self.curve[i] - district_voter_preferences[i]) ** 2 for i in range(self.num_districts)]) ** 0.5 #fitness is 2 * std dev of population + 60000 * variance between target curve and actual curve

    def get_edge_tiles(self, first_pass = True, flipped_tile = None, prev_edge_tiles = []): #get flippable edge tiles
        if first_pass: #if first iteration of algorithm, naively check every tile         
            edge_tiles = []
            for row in self.region.tiles:
                for tile in row:
                    edge_tile_data = []
                    #for each tile if neighbors are in different district, tile is an edge tile and can flip to that district. each tile can be bordering multiple districts so each item in edge tile list is [tile, district it can flip to, district it can flip to #2, ...]
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

        else: #if algorithm is not on first iteration, then a set of edge tiles has already been generated.  instead of naively checking every tile again, only check tiels in vincinity of flipped tile bc those are only tiles which could have been affected
            neighbours = [flipped_tile] #find neighboring tiles
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

            for tile in neighbours: #perform same steps as if first iteration but only on neighbor tiles
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

    def dfs(self, visited, node_on, district): #perform dfs on district of tile to be flipped to check if flipping the tile makes district non-continuous
        if len(visited) >= len(district):
            return True

        edges = [(1, 0), (0, 1), (-1, 0), (0, -1)]

        for edge in edges:
            if node_on.position[0] + edge[0] >= 0 and node_on.position[0] + edge[0] < self.region.dimensions[0] and node_on.position[1] + edge[1] >=0 and node_on.position[1] + edge[1] < self.region.dimensions[1]:
                if self.region.tiles[node_on.position[0] + edge[0]][node_on.position[1] + edge[1]].district == node_on.district and self.region.tiles[node_on.position[0] + edge[0]][node_on.position[1] + edge[1]] not in visited:
                    visited.append(self.region.tiles[node_on.position[0] + edge[0]][node_on.position[1] + edge[1]])    
                    if self.dfs(visited, self.region.tiles[node_on.position[0] + edge[0]][node_on.position[1] + edge[1]], district):
                        return True

        return False

    def check_if_continuous(self, district): #wrapper code for dfs, checks if flipping tile breaks continuity
        if len(district) == 0:
            return False

        return self.dfs([district[0]], district[0], district)

    def mcmc(self, iters): #simulated anneal based algorithm for gerrymandering
        self.voronoi_districts() #generate initial districting

        for i in range(iters):
            if i == 0: #get edge tiles naively
                edge_tiles = self.get_edge_tiles(True)
                overall_voter_preference = 0
                for row in region.tiles:
                    for tile in row:
                        overall_voter_preference += tile.voter_preference * tile.population
    
            elif use_from_eval: #use previously generated edge tiles
                edge_tiles = eval_edge_tiles
                use_from_eval = False

            else: 
                edge_tiles = self.get_edge_tiles(False, tile_to_flip[0], edge_tiles)

            tile_to_flip = random.choices(edge_tiles, weights = [len(edge_tile) for edge_tile in edge_tiles], k = 1)[0] #randomly choose tile to flip

            original_score = self.score_district(edge_tiles, True) # get score before flip

            if i == 0:
                print('Initial Score: ' + str(original_score))

            original_district = tile_to_flip[0].district

            tile_to_flip[0].district = random.choice(tile_to_flip[1:])
            self.districts[original_district].remove(tile_to_flip[0]) # flip tile

            if self.check_if_continuous(self.districts[original_district]):
                use_from_eval = True
                self.districts[tile_to_flip[0].district].append(tile_to_flip[0])
                eval_edge_tiles = self.get_edge_tiles(False, tile_to_flip[0], edge_tiles) # finish flipping tile
                new_score = self.score_district(eval_edge_tiles, True) 

                if original_score < new_score and random.random() >= 0.5 - 0.5 / iters * i: #if new districting worse, then undo with certain probability increasing as number of iterations increases
                    self.districts[original_district].append(tile_to_flip[0])
                    self.districts[tile_to_flip[0].district].remove(tile_to_flip[0])
                    tile_to_flip[0].district = original_district
                    use_from_eval = False

            else: #if not continuous undo
                tile_to_flip[0].district = original_district
                self.districts[original_district].append(tile_to_flip[0])
        
        print('Final Score: ' + str(self.score_district(edge_tiles)))

        self.region.display_region()
        district_count = 0
        for district in self.districts:
            district_result = 0
            for tile in district:
                district_result += tile.voter_preference * tile.population

            if district_result < 0:
                district_count -= 1
            else:
                district_count += 1

            print(district_result)
            self.region.display_region(True, district)

        print(district_count)
    




        


gerrymander = Gerrymander(region, 1, 6, [0.05, 0.05, 0.05, 0.05, 0.05, -0.3]) #to make algorithm favor party, set curve such that more numbers have same sign as that party, but with smaller magnitudes, and fewer with the sign of the opposite party but larger magnitudes.  this ensures more districts will be won by the favored party.
gerrymander.mcmc(10000) #run algorithm, more iters gives better result but takes longer