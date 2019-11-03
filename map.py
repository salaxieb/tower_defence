import pyglet
from pyglet.window import mouse
from time import time, sleep
from math import pi, radians, cos, sin, floor
import math


class Map_Tile:
    def __init__(self, pos, width, height):
        self.pos = pos
        self.width = width
        self.height = height

    def draw_bigger(self):
        width = self.width/2
        height = self.height/2
        width -= 3
        height -= 3
        method = pyglet.gl.GL_QUADS
        x = self.pos[0]
        y = self.pos[1]
        pyglet.graphics.draw(4, method, ('v2f', [
        x-width, y-height,
         x+width, y-height,
          x+width, y+height,
           x-width, y+height])), ('c3B', (50, 50, 50) * 4)

    def graphics(self):
        width = self.width/2
        height = self.height/2
        x = self.pos[0]
        y = self.pos[1]
        method = pyglet.gl.GL_LINES
        return 8, method, ('v2f',   [x-width, y-height, x+width, y-height,
                                    x+width, y-height,x+width, y+height,
                                    x+width, y+height, x-width, y+height,
                                    x-width, y+height,x-width, y-height]), ('c3B', (100, 100, 100) * 8)

class Start_Tile(Map_Tile):
    def graphics(self):
        width = self.width/2
        height = self.height/2
        width += 3
        height += 3
        method = pyglet.gl.GL_QUADS
        x = self.pos[0]
        y = self.pos[1]
        return 4, method, ('v2f', [
        x-width, y-height,
         x+width, y-height,
          x+width, y+height,
           x-width, y+height]), ('c3B', (50, 50, 50) * 4)

class Map:
    def __init__(self):
        self.gap = 4
        self.gap_x = 200
        self.gap_y = 400
        self.blocks_x = 15
        self.blocks_y = 7
        self.size_x = 40 * self.blocks_x
        self.size_y = 40 * self.blocks_y
        self.on_block = False
        self.on_block_i = -1
        self.on_block_j = -1
        self.block_width = (self.size_x - self.gap*(self.blocks_x))/self.blocks_x
        self.block_height = (self.size_y - self.gap*(self.blocks_y))/self.blocks_y
        self.blocks_arr = []
        self.changement_of_position = True
        self.start_positions = [(-1, int(self.blocks_y/2)),
                                (-1, 0),
                                (-1, self.blocks_y-1)]
        self.end_positions = [(self.blocks_x, int(self.blocks_y/2))]

        for i in range(self.blocks_x):
            self.blocks_arr.append([0] * self.blocks_y)
        for i in range(self.blocks_x):
            for j in range(self.blocks_y):
                pos = self.give_coordinates_of_block((i, j))
                b = Map_Tile(pos, self.block_width, self.block_height)
                self.blocks_arr[i][j] = b

        self.batch = pyglet.graphics.Batch()
        for i in range(self.blocks_x):
            for j in range(self.blocks_y):
                count, mode, *data = self.blocks_arr[i][j].graphics()
                self.batch.add(count, mode, None, data[0], data[-1])

        for start_pos in self.start_positions:
            pos = self.give_coordinates_of_block(start_pos)
            b = Start_Tile(pos, self.block_width, self.block_height)
            count, mode, *data = b.graphics()
            self.batch.add(count, mode, None, data[0], data[-1])

        for start_pos in self.end_positions:
            pos = self.give_coordinates_of_block(start_pos)
            b = Start_Tile(pos, self.block_width, self.block_height)
            count, mode, *data = b.graphics()
            self.batch.add(count, mode, None, data[0], data[-1])

    def give_coordinates_of_block(self, pos):
        pos_x = self.gap_x + self.gap/2 + self.block_width/2 + pos[0] * (self.block_width + self.gap)
        pos_y = self.gap_y + self.gap/2 + self.block_height/2 + pos[1] * (self.block_height + self.gap)
        return (pos_x, pos_y)

    def draw(self):
        self.batch.draw()
        if (self.on_block):
            self.blocks_arr[self.on_block_i][self.on_block_j].draw_bigger()

    def check_if_on_block(self, x, y, dx, dy):
        self.on_block, (self.on_block_i, self.on_block_j) = self.give_indexes_of_coordinates((x+dx/2, y+dy/2))

    def give_indexes_of_coordinates(self, pos):
        x = pos[0] - self.gap_x
        y = pos[1] - self.gap_y
        i = floor(x / (self.block_width + self.gap))
        j = floor(y / (self.block_height + self.gap))
        if (i <= self.blocks_x - 1 and i >= 0
         and j <= self.blocks_y - 1 and y >= 0):
          # and x - i * (self.block_width + self.gap) > self.gap/2
          #  and x - (i+1) * (self.block_width + self.gap) < self.gap/2):
            return True, (i, j)
        else:
            ### check if in theend
            if i == self.end_positions[0][0] and j == self.end_positions[0][1]:
                return False, self.end_positions[0]
            else:
                return False, (-1, -1)
