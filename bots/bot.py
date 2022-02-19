import sys

import random
import heapq

from src.player import *
from src.structure import *
from src.game_constants import GameConstants as GC

def compute_distances_from_cell(map,r,c):
    D = [[float('inf') for i in range(len(map[0]))] for j in range(len(map))]

    def set(r,c, val):
        if (r >= 0 and r < len(D)):
            if (c >= 0 and c < len(D[0])):
                D[r][c] = val
    set(r, c, 0)
    set(r-1, c, 0)
    set(r+1, c, 0)
    set(r, c-1, 0)
    set(r, c+1, 0)
    def compute_dist(r,c):
        return

class Cell():
    def __init__(self, r, c, passability, utility):
        self.r = r
        self.c = c
        self.passability = passability
        self.utility = utility

    def __hash__(self):
        return hash((r,c))
    def __eq__(self, other):
        return self.r == other.r and self.c == other.c

class MyPlayer(Player):
    def __init__(self):
        print("Init")
        self.turn = 0

        self.roads = set()
        self.towers = set()
        self.generators = set()

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
                        self.generators.add((r,c))

        for r in range(self.HEIGHT):
            for c in range(self.WIDTH):



    def play_turn(self, turn_num, map, player_info):
        if turn_num == 0:
            real_init(map, player_info)

        return
