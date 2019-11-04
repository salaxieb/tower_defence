from math import pi, radians, cos, sin, floor
import math
import pyglet
from time import time
import random


class Bullet:
    def __init__(self, speed, angle, pos, damage, life_time):
        self.speed = speed
        self.angle = angle
        self.pos = pos
        self.damage = damage
        self.radius = 3
        self.life_time = life_time
        self.born_time = time()
        self.deprecated = False
        num_points = 5
        self.cos_radius = [self.radius*cos(radians(float(i)/num_points * 360.0)) for i in range(num_points)]
        self.sin_radius = [self.radius*sin(radians(float(i)/num_points * 360.0)) for i in range(num_points)]

    def move(self, dt):
        if time() - self.born_time > self.life_time:
            self.deprecated = True
            return
        self.pos = (self.pos[0] + dt * self.speed * cos(self.angle),
        self.pos[1] + dt * self.speed * sin(self.angle))

    def is_intersects(self, enemies, towers):
        for enemy in enemies:
            if ((self.pos[0] - enemy.pos[0])**2 + (self.pos[1] - enemy.pos[1])**2) < enemy.radius**2:
                enemy.deal_damage(self.damage)
                self.deprecated = True
                return
                
        for tower in towers:
            if tower.inside_of_self(self.pos):
                tower.deal_damage(self.damage)
                self.deprecated = True
                return

    def give_circle(self, numPoints = 5):
        verts = []
        for cos_r, sin_r in zip(self.cos_radius, self.sin_radius):
            verts += [self.pos[0]+cos_r, self.pos[1]+sin_r]
        return pyglet.graphics.vertex_list(numPoints, ('v2f', verts), ('c3B', (155, 10, 10) * numPoints))

    def draw(self):
        self.give_circle().draw(pyglet.gl.GL_LINE_LOOP)
