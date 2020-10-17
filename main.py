import pyglet
from pyglet.window import mouse
from time import time, sleep
from pyglet.window import Window
from math import pi, radians, cos, sin, floor
import math
from map import Map
from enemies import Enemies
from towers import Towers, Tower, AttackTower, DefenceTower
from menu import Menu
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
        self.menu = Menu(self.map, self.towers, self.enemies, screen_width, screen_height)

        self.dragging_tower = False
        self.round = 1
        self.start_round()

    def start_round(self, round=0):
        difficulty = round + 3
        self.enemies.new_round(difficulty=difficulty)

    def round_traker(self):
        if all([enemy.deprecated==True or enemy.in_the_end==True for enemy in self.enemies.enemies]):
            self.round += 1
            self.start_round(round=self.round)

    def on_mouse_motion(self, x, y, dx, dy):
        self.map.on_mouse_motion(x, y, dx, dy)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.menu.on_mouse_drag(x, y, dx, dy, buttons, modifiers)

    def update(self, dt):
        self.round_traker()
        self.towers.update(dt, self.enemies)
        self.enemies.update(dt, self.towers)

    def user_text_draw(self):
        self.enemies_left = pyglet.text.Label(f'{len([enemy for enemy in self.enemies.enemies if not enemy.deprecated or enemy.in_the_end])} over {len(self.enemies.enemies)} enemies left',
                          font_name='Helvetica',
                          font_size=12,
                          x=window.width - 200, y=window.height- 100,
                          anchor_x='center', anchor_y='center')
        self.enemies_left.draw()

        self.round_nb = pyglet.text.Label(f'round {self.round}',
                          font_name='Helvetica',
                          font_size=12,
                          x=window.width - 200, y=window.height- 120,
                          anchor_x='center', anchor_y='center')
        self.round_nb.draw()

    def draw(self):
        window.clear()
        self.map.draw()
        self.towers.draw()
        self.enemies.draw()
        self.menu.draw()
        self.user_text_draw()

    def on_mouse_press(self, x, y, button, modifiers):
        self.menu.on_mouse_press(x, y)

    def on_mouse_release(self, x, y, button, modifiers):
        self.menu.on_mouse_release(x, y)

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

@window.event
def on_mouse_drag(x, y,  dx, dy, button, modifiers):
    game.on_mouse_drag(x, y,  dx, dy, button, modifiers)


def game_update(dt=0):
    game.update(dt)

def screen_update(dt=0):
    game.draw()

pyglet.clock.schedule_interval(screen_update, 1/60)
pyglet.clock.schedule_interval(game_update, 1/30)

pyglet.app.run()
