from math import pi, radians, cos, sin, floor
import math
import pyglet
from time import time
import random
from bullet import Bullet
import numpy as np

class Enemies():
    def __init__(self, map, towers):
        self.map = map
        self.start_positions = self.map.start_positions
        self.step_size = 20
        self.towers = towers
        self.enemies = []
        # start_positions = [self.map.give_coordinates_of_block(start) for start in self.map.start_positions]
        # ends = [self.map.give_coordinates_of_block(end) for end in self.map.end_positions]
        self.shortest_path(self.map.start_positions, self.map.end_positions[0])
        # self.shortest_path_pixels(start_positions, ends[0])

    def __iter__(self):
        for enemy in self.enemies:
            yield enemy

    def new_round(self, difficulty):
        for index, enemy in enumerate(self.enemies):
            if enemy.deprecated:
                self.enemies.pop(index)
        self.enemies = [Enemy(radius=5,
         health=100,
          damage=20,
           speed=40,
            shoot_range=80,
             attack_speed=2,
              pos=self.map.give_noisy_coordinates_of_block(random.choice(self.map.start_positions)))
               for i in range(difficulty)]

    def give_possible_steps(self, current, unvisited, starts, end):
        routes = []
        costs = []
        i = current[0]
        j = current[1]
        for [horizontal, vertical] in [[0, 1], [0, -1], [1, 0], [-1, 0]]:
            if self.reachable_condition(i+horizontal, j+vertical, starts, end):
                routes.append((i+horizontal, j+vertical))
                costs.append(1)# = math.sqrt(horizontal**2 + vertical**2))
                if self.towers.on_tower(i+horizontal, j+vertical):
                    average_attack = sum([enemy.damage for enemy in self.enemies if not enemy.deprecated])
                    if len([enemy.damage for enemy in self.enemies if not enemy.deprecated])==0:
                        average_attack = 1
                    else:
                        average_attack = average_attack/len([enemy.damage for enemy in self.enemies if not enemy.deprecated])
                    average_attack *= 40/2 ## *self.speed / self.attack_speed
                    costs[-1] += self.towers.give_health_of_tower(i+horizontal, j+vertical)/average_attack
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

        #print(self.dynamic_paths)
        #print(self.routes)
        #raise

    def reachable_condition(self, i, j, starts, end):
        in_map = (0 <= i < self.map.blocks_x and 0 <= j < self.map.blocks_y or (i, j) in starts or (i, j) == end)
        #on_tower = self.towers.on_tower(i, j)
        return in_map# and not on_tower

    def update(self, dt, towers):
        [e.move(dt, self.dynamic_paths, self.map, self.towers) for e in self.enemies]
        #[e.attack(towers) for e in self.enemies]
        [e.update(dt, self, towers) for e in self.enemies]

    def update_routes(self):
        self.shortest_path(self.map.start_positions, self.map.end_positions[0])

    def draw(self):
        [e.draw() for e in self.enemies]

class Enemy:
    def __init__(self, radius, health, damage, speed, shoot_range, attack_speed, pos):
        self.radius = radius
        self.health = health
        self.max_health = health
        self.damage = damage
        self.speed = speed
        self.shoot_range = shoot_range
        self.pos = pos
        self.bullets = []
        self.attack_speed = attack_speed
        self.last_shoot = -1
        self.deprecated = False
        self.in_the_end = False

        self.bounding_circle = []
        numPoints = 10
        print(numPoints)
        for i in range(numPoints):
            angle = radians(float(i)/numPoints * 360.0)
            x = self.radius*cos(angle)
            y = self.radius*sin(angle)
            self.bounding_circle += [x,y]

    def inside_of_self(self, pos):
        if ((pos[0] - self.pos[0])**2 + (pos[1] - self.pos[1])**2) < self.radius**2:
            return True
        return False

    def deal_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.deprecated = True

    def attack(self, towers):
        if not self.deprecated:
            if time() - self.last_shoot > 1/self.attack_speed:
                target_tower = False
                for tower in towers:
                    if self.in_shooting_range(tower) and not tower.deprecated:
                        target_tower = tower
                if target_tower:
                    angle = math.atan2(target_tower.pos[1] - self.pos[1], target_tower.pos[0] - self.pos[0])
                    self.last_shoot = time()
                    self.shoot(angle, towers)

    def in_shooting_range(self, tower):
        if ((self.pos[0] - tower.pos[0])**2 + (self.pos[1] - tower.pos[1])**2) < self.shoot_range**2:
            return True
        return False

    def shoot(self, angle, towers):
        angle = angle + 0.2 * (random.random() - 0.5)
        self.bullets.append(Bullet(speed=200, angle=angle, pos=self.pos, damage=3, life_time=self.shoot_range/200, targets=towers))

    def move(self, dt, dynamic_routes, map, towers):
        if not self.deprecated:
            on_block, map_tile_coordinates = map.give_indexes_of_coordinates(self.pos)
            if map_tile_coordinates in map.end_positions:
                self.in_the_end = True
                return
            move_to_coordinates = dynamic_routes[map_tile_coordinates][1]
            move_to = map.give_coordinates_of_block(move_to_coordinates)
            if towers.on_tower(move_to_coordinates[0], move_to_coordinates[1]):
                tower = towers.give_tower(move_to_coordinates[0], move_to_coordinates[1])
                self.attack([tower])
            else:
                angle = math.atan2(move_to[1] - self.pos[1], move_to[0] - self.pos[0])
                self.pos = (self.pos[0] + self.speed * dt * cos(angle),
                self.pos[1] + self.speed * dt * sin(angle))

    def update(self, dt, enemies, towers):
        for index, bullet in enumerate(self.bullets):
            if bullet.deprecated:
                self.bullets.pop(index)
            else:
                bullet.move(dt)
                bullet.is_intersects()

    def give_circle(self, numPoints = 10):
        verts = [x + self.pos[i%2] for i, x in enumerate(self.bounding_circle)]
        if not self.deprecated:
            return pyglet.graphics.vertex_list(numPoints, ('v2f', verts), ('c3B', (255, 100, 100) * numPoints))
        return pyglet.graphics.vertex_list(numPoints, ('v2f', verts), ('c3B', (100, 100, 100) * numPoints))

    def draw(self):
        #health bar
        width = self.health/self.max_health * self.radius * 2
        width = max(width, 0)
        height = 2
        method = pyglet.gl.GL_QUADS
        x = self.pos[0] - self.radius
        y = self.pos[1] + self.radius + 2
        pyglet.graphics.draw(4, method, ('v2f', [
            x, y,
                x+width, y,
                    x+width, y+height,
                        x, y+height]), ('c3B', (250, 20, 20) * 4))

        for index, bullet in enumerate(self.bullets):
            bullet.draw()
        self.give_circle().draw(pyglet.gl.GL_LINE_LOOP)
