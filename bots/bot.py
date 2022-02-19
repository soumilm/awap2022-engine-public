import sys
from math import *

import random
import heapq

from src.player import *
from src.structure import *
from src.game_constants import GameConstants as GC

def in_bounds(D, r,c):
    if (r >= 0 and r < len(D)):
        return (c >= 0 and c < len(D[0]))
    return False

def get_neighbors(map, r,c):
    offsets = [(1,0), (0,1), (-1, 0), (0, -1)]
    return [(r+i, c+j) for i,j in offsets if in_bounds(map, r+i, c+j)]

def compute_distances_from_cell(map, row, col):
    D = [[float('inf') for i in range(len(map[0]))] for j in range(len(map))]

    def set_value(r,c, val, path):
        if (r >= 0 and r < len(D)):
            if (c >= 0 and c < len(D[0])):
                D[r][c] = (val, path)
    def get(r,c):
        if (r >= 0 and r < len(D)):
            if (c >= 0 and c < len(D[0])):
                return D[r][c]
        return float('inf')
    def get_passability(r,c):
        if r == row and c == col: return 0

        if (r >= 0 and r < len(D)):
            if (c >= 0 and c < len(D[0])):
                return map[r][c].passability
        return float('inf')

    set_value(row, col, 0, [(row, col)])

    heap = [(0, (row, col), [(row, col)])]
    visited = set()
    while len(heap) > 0:
        (cost, (r,c), path) = heapq.heappop(heap)
        if ((r,c) in visited): continue

        visited.add((r,c))
        set_value(r,c, cost, path)

        for new_r, new_c in [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]:
            if ((new_r, new_c) not in visited and in_bounds(D, new_r, new_c)):
                new_cost = cost + get_passability(r,c)
                heapq.heappush(heap, (new_cost, (new_r, new_c), path + [(new_r, new_c)]))

    return D

def reachable_utility(map, r, c):
    offsets = [(i,j) for i in range(-2, 3) for j in range(-2, 3) if abs(i)+abs(j) <= 2]
    total = 0
    cities = set()
    for i,j in offsets:
        new_r = r + i;
        new_c = c + j
        if (in_bounds(map, new_r, new_c)):
            population = map[new_r][new_c].population
            total += population
            if population > 0:
                cities.add((new_r, new_c))
    return (total, cities)

class Cell():
    def __init__(self, r, c, dist, passability, utility, cities_covered):
        self.r = r
        self.c = c
        self.dist = dist
        self.passability = passability
        self.utility = utility
        self.cities_covered = cities_covered

    def __hash__(self):
        return hash((r,c))
    def __lt__(self, other):
        return self.priority() < other.priority()

    def __str__(self):
        return f"({self.r}, {self.c})"

    def priority(self):
        if self.utility == 0: return float('inf')
        else:
            return (self.dist + self.passability)/2 - self.utility

    def output_tuple(self):
        return (self.priority(), self)

class MyPlayer(Player):
    def __init__(self):
        self.turn = 0

        self.generators = set()
        self.structures = set()

        self.cities_covered = set()
        self.focus = None
        self.heap = []

    def real_init(self, map, player_info):
        self.HEIGHT = len(map)
        self.WIDTH = len(map[0])

        for r in range(self.HEIGHT):
            for c in range(self.WIDTH):
                tile = map[r][c]
                if tile.structure is not None:
                    team = tile.structure.team
                    tile_type = tile.structure.type
                    if (team == player_info.team and tile_type == StructureType.GENERATOR):
                        self.generators.add((r, c))
                        self.structures.add((r, c))

        gen_r, gen_c = list(self.generators)[0]
        mins = compute_distances_from_cell(map, gen_r, gen_c)
        for gen_r, gen_c in self.generators:
            D = compute_distances_from_cell(map, gen_r, gen_c)
            mins = [[min(mins[r][c], D[r][c]) for c in range(len(D[0]))] for r in range(len(D))]

        for r in range(self.HEIGHT):
            for c in range(self.WIDTH):
                utility, cities_covered = reachable_utility(map, r, c)
                cell = Cell(r,c, mins[r][c][0], map[r][c].passability, utility, cities_covered)
                heapq.heappush(self.heap, cell.output_tuple())

    def get_path(self, map, player_info, src):
        frontier_set = set([(src.r, src.c)])
        frontier = [(0, src.r, src.c, [(src.r, src.c)])]
        visited = set()
        while frontier:
            (cost, r, c, path) = heapq.heappop(frontier)
            frontier_set.remove((r,c))
            if (r,c) in self.structures:
                print("Found:", r, c)
                return (cost, r,c, path)
            visited.add((r,c))
            neighbors = get_neighbors(map, r, c)
            for (new_r, new_c) in neighbors:
                if (new_r, new_c) not in (visited | frontier_set):
                    frontier_set.add((new_r, new_c))
                    passability = map[r][c].passability
                    bigass_tuple = (cost + passability, new_r, new_c, path + [(new_r, new_c)])
                    heapq.heappush(frontier, bigass_tuple)

    def play_turn(self, turn_num, map, player_info):
        if turn_num == 0:
            self.real_init(map, player_info)

        print("Focus:",self.focus)
        while self.focus is None and len(self.heap) > 0:
            new_focus = heapq.heappop(self.heap)[1]
            if len(new_focus.cities_covered - self.cities_covered) > 0:
                self.focus = new_focus

        if self.focus is None: return

        path_tuple = self.get_path(map, player_info, self.focus)
        print("Shortest Path: ", path_tuple)
        shortest_path = path_tuple[-1][::-1]
        length = len(shortest_path)

        actual_money = player_info.money
        for i in range(length):
            r,c = shortest_path[i]
            cell = map[r][c]
            if i == length - 1:
                cost = 250 * cell.passability
                struct = StructureType.TOWER
            else:
                cost = 10 * cell.passability
                struct = StructureType.ROAD

            if cost < actual_money:
                self.build(struct, r,c)
                self.structures.add((r,c))
                actual_money -= cost
                if struct == StructureType.TOWER:
                    self.cities_covered |= self.focus.cities_covered
                    self.focus = None
            else:
                break

