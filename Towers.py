from Bullet import Bullet
import pyglet
from math import pi, radians, cos, sin, floor
import math
import random
from time import time

class Towers:
    def __init__(self, map):
        self.map = map
        self.towers =[]
        self.towers_batch = pyglet.graphics.Batch()
        self.buildable_towers = [AttackTower, DefenceTower, Tower]

        for i in range(self.map.blocks_x):
            self.towers.append([0] * self.map.blocks_y)
        for i in range(self.map.blocks_x):
            for j in range(self.map.blocks_y):
                t = False
                if (j > 0 and i == 3) or (j < 3 and i == 5):
                    self.tower_constructor(self.map.blocks_arr[i][j].pos, random.choice([Tower, DefenceTower, AttackTower]))
        for tower in self:
            if tower:
                count, mode, *data = tower.graphics()
                self.towers_batch.add(count, mode, None, data[0], data[-1])

        ### creating example tower ###
        # self.example_tower = Tower(pos = (1200, 600), width=self.map.block_width, height=self.map.block_height, range=0)
        # count, mode, *data = self.example_tower.graphics()
        # self.towers_batch.add(count, mode, None, data[0], data[-1])
        self.draw()

    def on_tower(self, i, j):
        if i < self.map.blocks_x and j < self.map.blocks_y:
            if self.towers[i][j] and not self.towers[i][j].deprecated:
                return True
            else:
                return False
        return False

    def give_tower(self, i, j):
        if i < self.map.blocks_x and j < self.map.blocks_y:
            if self.towers[i][j]:
                return self.towers[i][j]
            else:
                return False
        return False

    def tower_constructor(self, pos, Tower):
        on_block, (i, j) = self.map.give_indexes_of_coordinates(pos)
        if on_block:
            t = Tower(pos=self.map.blocks_arr[i][j].pos, width=self.map.block_width+1, height=self.map.block_height+1, range=150, health=200, damage=1)
            count, mode, *data = t.graphics()
            self.towers_batch.add(count, mode, None, data[0], data[-1])
            self.towers[i][j] = t

    def give_health_of_tower(self, i, j):
        if self.towers[i][j] != False:
            return self.towers[i][j].health
        else:
            return 0

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
                    self.shoot(angle, enemies)

    def in_shooting_range(self, enemy):
        if ((self.pos[0] - enemy.pos[0])**2 + (self.pos[1] - enemy.pos[1])**2) < self.range**2:
            return True
        return False

    def inside_of_self(self, pos):
        if (self.pos[0] - self.width/2 <= pos[0] <= self.pos[0] + self.width/2 and
        self.pos[1] - self.height/2 <= pos[1] <= self.pos[1] + self.height/2):
            return True
        return False

    def shoot(self, angle, enemies):
        angle = angle + 0.02 * (random.random() - 0.5)
        self.bullets.append(Bullet(speed=100, angle=angle, pos=self.pos, damage=20, life_time=self.range/100, targets=enemies))

    def update(self, dt, enemies, towers):
        self.attack(enemies)
        for index, bullet in enumerate(self.bullets):
            if bullet.deprecated:
                self.bullets.pop(index)
            else:
                bullet.move(dt)
                bullet.is_intersects()

    def draw(self):
        #health bar
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
        #gray version of tower
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

class AttackTower(Tower):
    def __init__(self, pos, width, height, range, health=1000, attack_speed=10, damage=3):
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

    def shoot(self, angle, enemies):
        angle = angle + 0.02 * (random.random() - 0.5)
        self.bullets.append(Bullet(speed=300, angle=angle, pos=self.pos, damage=20, life_time=self.range/300, targets=enemies))

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
           x-width, y+height]), ('c3B', (150, 50, 50) * 4)

class DefenceTower(Tower):
    def __init__(self, pos, width, height, range, health=10000, attack_speed=0, damage=0):
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

    def attack(self, enemies):
        pass

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
           x-width, y+height]), ('c3B', (50, 150, 50) * 4)
