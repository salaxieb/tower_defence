from Bullet import Bullet
from map import Map
import pyglet
from math import pi, radians, cos, sin, floor
import math
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
                    t = Tower(pos=self.map.blocks_arr[i][j].pos, width=self.map.block_width+2, height=self.map.block_height+2, range=150, health=1000, damage=1)
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
            t = Tower(pos=self.map.blocks_arr[i][j].pos, width=self.map.block_width+5, height=self.map.block_height+5, range=150, health=200, damage=1)
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
        [tower.draw() for tower in self]

    def update(self, dt, enemies):
        for tower in self:
            if tower:
                tower.update(dt, enemies, self)

    def on_example_tower(self, x, y):
        pos_x = self.example_tower.pos[0]
        pos_y = self.example_tower.pos[1]
        width = self.example_tower.width/2
        height = self.example_tower.height/2
        if pos_x-width <= x <= pos_x+width and pos_y-height <= y <= pos_y+height:
            return True
        return False



class Tower:
    def __init__(self, pos, width, height, range, health=1000, attack_speed=1, damage=1):
        self.pos = pos
        self.health = health
        self.max_health = self.health
        self.attack_speed = attack_speed
        self.damage = damage
        self.width = width
        self.height = height
        self.range = range
        self.bullets = []
        self.last_shoot = -1
        self.deprecated = False

    def deal_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.deprecated = True

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

    def attack(self, enemies):
        if not self.deprecated:
            if time() - self.last_shoot > 1/self.attack_speed:
                target_enemy = False
                for enemy in enemies:
                    if self.in_shooting_range(enemy) and not enemy.deprecated:
                        target_enemy = enemy
                        break
                if target_enemy:
                    angle = math.atan2(target_enemy.pos[1] - self.pos[1], target_enemy.pos[0] - self.pos[0])
                    self.last_shoot = time()
                    self.shoot(angle)

    def in_shooting_range(self, enemy):
        if ((self.pos[0] - enemy.pos[0])**2 + (self.pos[1] - enemy.pos[1])**2) < self.range**2:
            return True
        return False

    def inside_of_self(self, pos):
        if (self.pos[0] - self.width/2 <= pos[0] <= self.pos[0] + self.width/2 and
        self.pos[1] - self.height/2 <= pos[1] <= self.pos[1] + self.height/2):
            return True
        return False

    def shoot(self, angle):
        angle = angle + 0.02 * (random.random() - 0.5)
        self.bullets.append(Bullet(500, angle, self.pos, 2, self.range/500))

    def update(self, dt, enemies, towers):
        self.attack(enemies)
        for index, bullet in enumerate(self.bullets):
            if bullet.deprecated:
                self.bullets.pop(index)
            else:
                bullet.move(dt)
                bullet.is_intersects(enemies, towers)

    def draw(self):
        width = self.health/self.max_health * self.width
        width = max(width, 0)
        height = 4
        method = pyglet.gl.GL_QUADS
        x = self.pos[0] - self.width/2
        y = self.pos[1] + self.height/2 + 2
        pyglet.graphics.draw(4, method, ('v2f', [
            x, y,
                x+width, y,
                    x+width, y+height,
                        x, y+height]), ('c3B', (250, 20, 20) * 4))
        if self.deprecated:
            width = self.width/2
            height = self.height/2
            method = pyglet.gl.GL_QUADS
            x = self.pos[0]
            y = self.pos[1]
            pyglet.graphics.draw(4, method, ('v2f', [
            x-width, y-height,
             x+width, y-height,
              x+width, y+height,
               x-width, y+height]), ('c3B', (50, 50, 50) * 4))

        for bullet in self.bullets:
            bullet.draw()
