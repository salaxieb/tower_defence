import pyglet
from pyglet.window import mouse
from time import time, sleep
from math import pi, radians, cos, sin, floor
import math
import random

class Menu:
    def __init__(self, Map, Towers, Enemies, screen_width, screen_height):
        self.map = Map
        self.towers = Towers
        self.enemies = Enemies
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.dragging_tower = False
        self.batch = pyglet.graphics.Batch()
        self.example_towers = []
        example_tower_pos = [100, screen_height-100]
        for tower in Towers.buildable_towers:
            self.example_towers.append(tower(pos = tuple(example_tower_pos), width=self.map.block_width, height=self.map.block_height, range=0))
            count, mode, *data = self.example_towers[-1].graphics()
            self.batch.add(count, mode, None, data[0], data[-1])
            example_tower_pos[0] += self.map.block_width + 10

    def on_mouse_press(self, x, y):
        # self.check_if_on_example_tower
        for tower in self.example_towers:
            if tower.inside_of_self((x, y)):
                self.dragging_tower = tower
                break

    def on_mouse_release(self, x, y):
        if self.dragging_tower != False and self.map.give_indexes_of_coordinates((x,y))[0]:
            self.towers.tower_constructor((x, y), type(self.dragging_tower))
            self.enemies.update_routes()
        self.dragging_tower = False

    def draw(self):
        self.batch.draw()
