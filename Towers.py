from Bullet import Bullet
from map import Map
import pyglet
from math import pi, radians, cos, sin, floor
import random
from time import time

class Towers:
    def __init__(self, map):
        self.map = map
        self.towers =[]
        for i in range(self.map.blocks_x):
            self.towers.append([0] * self.map.blocks_y)
        for i in range(self.map.blocks_x):
            for j in range(self.map.blocks_y):
                t = False
                if (j > 0 and i == 3) or (j < 3 and i == 5):
                    t = Tower(pos=self.map.blocks_arr[i][j].pos, width=self.map.block_width+5, height=self.map.block_height+5, range=500, health=200, damage=1)
                self.towers[i][j] = t
        self.towers_batch = pyglet.graphics.Batch()
        for tower in self:
            if tower:
                count, mode, *data = tower.graphics()
                self.towers_batch.add(count, mode, None, data[0], data[-1])

        ### creating example tower ###
        self.example_tower = Tower(pos = (1200, 600), width=self.map.block_width, height=self.map.block_height, range=0)
        count, mode, *data = self.example_tower.graphics()
        self.towers_batch.add(count, mode, None, data[0], data[-1])
        self.draw()

    def on_tower(self, i, j):
        if i < self.map.blocks_x and j < self.map.blocks_y:
            if self.towers[i][j]:
                return True
            else:
                return False
        return False

    def tower_constructor(self, pos):
        on_block, (i, j) = self.map.give_indexes_of_coordinates(pos)
        if on_block:
            t = Tower(pos=self.map.blocks_arr[i][j].pos, width=self.map.block_width+5, height=self.map.block_height+5, range=500, health=200, damage=1)
            count, mode, *data = t.graphics()
            self.towers_batch.add(count, mode, None, data[0], data[-1])
            self.towers[i][j] = t

    def __iter__(self):
        for towers_arr in self.towers:
            for tower in towers_arr:
                if tower:
                    yield tower

    def draw(self):
        self.towers_batch.draw()
        [tower.draw_bullets() for tower in self]

    def update(self, dt):
        for tower in self:
            if tower:
                tower.shoot()
                tower.update(dt)

    def on_example_tower(self, x, y):
        pos_x = self.example_tower.pos[0]
        pos_y = self.example_tower.pos[1]
        width = self.example_tower.width/2
        height = self.example_tower.height/2
        if pos_x-width <= x <= pos_x+width and pos_y-height <= y <= pos_y+height:
            return True
        return False



class Tower:
    def __init__(self, pos, width, height, range, health=100, attack_speed=0.2, damage=1):
        self.pos = pos
        self.health = health
        self.attack_speed = attack_speed
        self.damage = damage
        self.width = width
        self.height = height
        self.range = range
        self.bullets = []
        self.last_shoot = -1

    def graphics(self):
        width = self.width/2
        height = self.height/2
        method = pyglet.gl.GL_QUADS
        x = self.pos[0]
        y = self.pos[1]
        return 4, method, ('v2f', [
        x-width, y-height,
         x+width, y-height,
          x+width, y+height,
           x-width, y+height]), ('c3B', (50, 50, 150) * 4)

    def shoot(self):
        angle = pi + pi/6 + 0.02 * (random.random() - 0.5)
        if time() - self.last_shoot > 1/self.attack_speed:
            self.last_shoot = time()
            self.bullets.append(Bullet(100, angle, self.pos, 2, self.range/200))

    def update(self, dt):
        for index, bullet in enumerate(self.bullets):
            if bullet.deprecated:
                self.bullets.pop(index)
            else:
                bullet.move(dt)

    def draw_bullets(self):
        for bullet in self.bullets:
            bullet.draw()
