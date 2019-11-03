from math import pi, radians, cos, sin, floor
import math
import pyglet
from time import time
import random
from Bullet import Bullet
import numpy as np

class Enemies():
    def __init__(self, map, towers):
        self.map = map
        self.start_positions = self.map.start_positions
        self.step_size = 20
        self.towers = towers
        # start_positions = [self.map.give_coordinates_of_block(start) for start in self.map.start_positions]
        # ends = [self.map.give_coordinates_of_block(end) for end in self.map.end_positions]
        self.shortest_path(self.map.start_positions, self.map.end_positions[0])
        # self.shortest_path_pixels(start_positions, ends[0])
        self.enemies = [Enemy(radius=5,
         health=20,
          damage=20,
           speed=self.step_size,
            range=200,
             attack_speed=0.5,
              pos=self.map.give_coordinates_of_block(i))
               for i in self.routes]

    def give_possible_steps(self, current, unvisited, starts, end):
        routes = []
        costs = []
        i = current[0]
        j = current[1]
        for [horizontal, vertical] in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
            if self.reachable_condition(i+horizontal, j+vertical, starts, end):
                routes.append((i+horizontal, j+vertical))
                costs.append(math.sqrt(horizontal**2 + vertical**2))
        return routes, costs

    def give_next_step(self, unvisited, dynamic_paths):
        clothest = np.inf
        for tile in unvisited:
            if dynamic_paths[tile][0] < clothest:
                next_tile = tile
                clothest = dynamic_paths[tile][0]
        return next_tile

    def shortest_path(self, starts, end):
        base_cost = 1
        dynamic_paths = {}
        unvisited = set()
        for i in range(-1, self.map.blocks_x):
            for j in range(-1, self.map.blocks_y):
                if self.reachable_condition(i, j, starts, end):
                    dynamic_paths[(i, j)] = (np.inf, -1)
                    unvisited.add((i, j))

        dynamic_paths[end] = (0, -1)
        unvisited.add(end)
        for start in starts:
            dynamic_paths[start] = (np.inf, -1)
            unvisited.add(start)

        while len(unvisited) != 0:
            current_pos = self.give_next_step(unvisited, dynamic_paths)
            unvisited.remove(current_pos)
            possible_routes, costs = self.give_possible_steps(current_pos, unvisited, starts, end)
            for next_step, cost in zip(possible_routes, costs):
                route_cost = dynamic_paths[current_pos][0] + cost
                if route_cost < dynamic_paths[next_step][0]:
                    dynamic_paths[next_step] = (route_cost, current_pos)
        ## backtraking
        routes = []
        for start in starts:
            next_step = start
            while next_step != end:
                routes.append(dynamic_paths[next_step][1])
                next_step = dynamic_paths[next_step][1]

        self.dynamic_paths = dynamic_paths
        self.routes = routes

    def triangle_situation(prev_0, prev_1, current):
        # csse_1
        # xs
        # xx
        # case_2
        # sx
        # xx
        # case_3
        # xx
        # sx
        # case_4
        # xx
        # xs
        # case 1 & case 2
        if prev_0[1] == prev_1[1] and abs(prev_0[0]-prev_1[0]) == 1:
            pass

    def reachable_condition(self, i, j, starts, end):
        in_map = (0 <= i < self.map.blocks_x and 0 <= j < self.map.blocks_y or (i, j) in starts or (i, j) == end)
        on_tower = self.towers.on_tower(i, j)
        return in_map and not on_tower

    def give_possible_steps_pixels(self, current, unvisited, starts, end):
        routes = []
        costs = []
        i = current[0]
        j = current[1]
        for [horizontal, vertical] in [[0, self.step_size], [0, -self.step_size],
         [self.step_size, 0], [-self.step_size, 0],
          [self.step_size, self.step_size], [-self.step_size, -self.step_size],
           [self.step_size, -self.step_size], [-self.step_size, self.step_size]]:
            # [20, -self.step_size], [20, 0], [20, self.step_size], [-20, -self.step_size], [-20, 0], [-20, self.step_size],
            # [-self.step_size, 20], [0, 20], [self.step_size, 20], [-self.step_size, -20], [0, -20], [self.step_size, -20],
            # [-20, -20], [20, 20], [20, -20], [-20, 20]]:
            if self.reachable_condition(i+horizontal, j+vertical, starts, end):
                routes.append((i+horizontal, j+vertical))
                costs.append(math.sqrt(horizontal**2 + vertical**2))
        # routes = [route for route in routes if route in unvisited]
        return routes, costs

    def give_next_step_pixels(self, unvisited, dynamic_paths):
        clothest = np.inf
        for tile in unvisited:
            if dynamic_paths[tile][0] < clothest:
                next_tile = tile
                clothest = dynamic_paths[tile][0]
        return next_tile

    def shortest_path_pixels(self, starts, end):
        base_cost = 1
        dynamic_paths = {}
        unvisited = set()
        for i in range(-40, self.map.size_x + 40, 1):
            for j in range(-40, self.map.size_y + 40, 1):
                if self.reachable_condition(self.map.gap_x+i,self.map.gap_y+j, end):
                    dynamic_paths[(self.map.gap_x+i, self.map.gap_y+j)] = (np.inf, -1)
                    unvisited.add((self.map.gap_x+i, self.map.gap_y+j))

        dynamic_paths[end] = (0, -1)
        unvisited.add(end)
        for start in starts:
            if self.reachable_condition(start[0],start[1], end):
                dynamic_paths[start] = (np.inf, -1)
                unvisited.add(start)

        while len(unvisited) != 0:
            current_pos = self.give_next_step_pixels(unvisited, dynamic_paths)
            unvisited.remove(current_pos)
            possible_routes, costs = self.give_possible_steps_pixels(current_pos, unvisited, starts, end)
            for next_step, cost in zip(possible_routes, costs):
                route_cost = dynamic_paths[current_pos][0] + cost
                if route_cost < dynamic_paths[next_step][0]:
                    dynamic_paths[next_step] = (route_cost, current_pos)
        #backtracking
        routes = []
        for start in starts:
            next_step = start
            while next_step != end:
                routes.append(dynamic_paths[next_step][1])
                next_step = dynamic_paths[next_step][1]
        self.dynamic_paths = dynamic_paths
        self.routes = routes

    def update(self, dt, towers):
        [e.move(dt, self.dynamic_paths, self.map) for e in self.enemies]
        [e.attack(towers) for e in self.enemies]
        [e.update(dt) for e in self.enemies]

    def update_routes(self):
        self.shortest_path(self.map.start_positions, self.map.end_positions[0])
        self.enemies = [Enemy(radius=5,
         health=20,
          damage=20,
           speed=self.step_size,
            range=200,
             attack_speed=5 + 1,
              pos=self.map.give_coordinates_of_block(i))
               for i in self.routes]

    def draw(self):
        [e.draw() for e in self.enemies]


class Enemy:
    def __init__(self, radius, health, damage, speed, range, attack_speed, pos):
        self.radius = radius
        self.health = health
        self.damage = damage
        self.speed = speed
        self.range = range
        self.pos = pos
        self.bullets = []
        self.attack_speed = attack_speed
        self.last_shoot = -1

    def attack(self, towers):
        if time() - self.last_shoot > 1/self.attack_speed:
            target_tower = False
            for tower in towers:
                if self.in_shooting_range(tower):
                    target_tower = tower
            if target_tower:
                angle = math.atan2(target_tower.pos[1] - self.pos[1], target_tower.pos[0] - self.pos[0])
                self.last_shoot = time()
                self.shoot(angle)

    def in_shooting_range(self, tower):
        if ((self.pos[0] - tower.pos[0])**2 + (self.pos[1] - tower.pos[1])**2) < self.range**2:
            return True
        return False



    def shoot(self, angle):
        angle = angle + 0.2 * (random.random() - 0.5)
        self.bullets.append(Bullet(200, angle, self.pos, 2, self.range/200))

    def move(self, dt, dynamic_routes, map):
        on_block, map_tile_coordinates = map.give_indexes_of_coordinates(self.pos)
        if map_tile_coordinates in map.end_positions:
            return
        move_to = dynamic_routes[map_tile_coordinates][1]
        move_to = map.give_coordinates_of_block(move_to)
        angle = math.atan2(move_to[1] - self.pos[1], move_to[0] - self.pos[0])
        self.pos = (self.pos[0] + self.speed * dt * cos(angle),
        self.pos[1] + self.speed * dt * sin(angle))

    def update(self, dt):
        for index, bullet in enumerate(self.bullets):
            if bullet.deprecated:
                self.bullets.pop(index)
            else:
                bullet.move(dt)

    def give_circle(self, numPoints = 10):
        verts = []
        for i in range(numPoints):
            angle = radians(float(i)/numPoints * 360.0)
            x = self.radius*cos(angle) + self.pos[0]
            y = self.radius*sin(angle) + self.pos[1]
            verts += [x,y]
        return pyglet.graphics.vertex_list(numPoints, ('v2f', verts), ('c3B', (255, 100, 100) * numPoints))

    def draw(self):
        for index, bullet in enumerate(self.bullets):
            bullet.draw()
        self.give_circle().draw(pyglet.gl.GL_LINE_LOOP)