import pyglet
from pyglet.window import mouse
from time import time, sleep
from pyglet.window import Window
from math import pi, radians, cos, sin, floor
import math
from map import Map
from Enemies import Enemies
from Towers import Towers, Tower
from pyglet.window import mouse

screen_width = 1280
screen_height = 960
window = Window(width=screen_width, height=screen_height)
window.set_mouse_visible(True)
# window.set_fullscreen(True)

class Game:
    def __init__(self):
        self.map = Map()
        self.towers = Towers(self.map)
        self.enemies = Enemies(self.map, self.towers)
        self.dragging_tower = False

    def on_mouse_motion(self, x, y, dx, dy):
        self.map.check_if_on_block(x, y, dx, dy)

    def update(self, dt):
        self.towers.update(dt, self.enemies)
        self.enemies.update(dt, self.towers)

    def draw(self):
        window.clear()
        self.map.draw()
        self.enemies.draw()
        self.towers.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.towers.on_example_tower(x,y):
            self.dragging_tower = True

    def on_mouse_release(self, x, y, button, modifiers):
        self.dragging_tower = False
        self.towers.tower_constructor((x, y))
        self.enemies.update_routes()


game = Game()

@window.event
def on_mouse_motion(x, y, dx, dy):
    game.on_mouse_motion(x, y, dx, dy)

@window.event
def on_mouse_press(x, y, button, modifiers):
    game.on_mouse_press(x, y, button, modifiers)

@window.event
def on_mouse_release(x, y, button, modifiers):
    game.on_mouse_release(x, y, button, modifiers)


def game_update(dt=0):
    pass
    game.update(dt)

def screen_update(dt=0):
    game.draw()

pyglet.clock.schedule_interval(screen_update, 1/60)
pyglet.clock.schedule_interval(game_update, 1/30)

pyglet.app.run()
