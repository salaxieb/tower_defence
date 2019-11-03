import pyglet
from pyglet.window import mouse
from time import time, sleep
from pyglet.window import Window
from math import pi, radians, cos, sin

screen_width = 640
screen_height = 480
window = Window(width=screen_width, height=screen_height)
window.set_mouse_visible(False)

class Wall:
    def __init__(self, type, pos_x=0, pos_y=screen_height/2, width=10, height=100):
        self.type = type
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = width
        self.height = height

    def mouse_move(self, x=screen_width-10, y=screen_height/2, dx=0, dy=0):
        x = x + dx
        self.pos_x = x
        y = y + dy
        self.pos_y = y

    def draw(self):
        x = self.pos_x
        y = self.pos_y
        pyglet.graphics.draw(4, pyglet.gl.GL_QUADS, ('v2f', [
        x-self.width/2, y-self.height/2,
         x+self.width/2,  y-self.height/2,
          x+self.width/2, y+self.height/2,
           x-self.width/2, y+self.height/2]))

class Ball:
    def __init__(self, speed=500, angle=pi/6, pos_x=screen_width/2, pos_y=screen_height/2, radius=3):
        self.speed = speed
        self.angle = angle
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.radius = radius

    def move(self, dt):
        self.pos_x += dt * self.speed * cos(self.angle)
        self.pos_y += dt * self.speed * sin(self.angle)

    def give_circle(self, numPoints = 20):
        verts = []
        for i in range(numPoints):
            angle = radians(float(i)/numPoints * 360.0)
            x = self.radius*cos(angle) + self.pos_x
            y = self.radius*sin(angle) + self.pos_y
            verts += [x,y]
        return pyglet.graphics.vertex_list(numPoints, ('v2f', verts))

    def draw(self):
        self.give_circle().draw(pyglet.gl.GL_LINE_LOOP)

player = Wall('ver')
top = Wall('hor', pos_x = screen_width/2, pos_y = screen_height, width = screen_width, height = 10)
bottom = Wall('hor', pos_x = screen_width/2, pos_y = 0, width = screen_width, height = 10)
left = Wall('ver', pos_x = 0, pos_y = screen_height/2, width = 10, height = screen_height)
right = Wall('ver', pos_x = screen_width, pos_y = screen_height/2, width = 10, height = screen_height)
computer = Wall('ver', pos_x = 630)
ball = Ball()

@window.event
def on_mouse_motion(x, y, dx, dy):
    player.mouse_move(x, y, dx, dy)
    intersection_check(player, ball)

def intersection_check(wall, ball):
    if abs(wall.pos_x - ball.pos_x) < (wall.width/2 + ball.radius) and abs(wall.pos_y - ball.pos_y) < (wall.height/2 + ball.radius):
        if wall.type == 'ver':
            ball.angle = pi - ball.angle
        if wall.type == 'hor':
            ball.angle = 2*pi - ball.angle

def update(dt):
    window.clear()
    ball.move(dt)
    computer.mouse_move(y = ball.pos_y)
    intersection_check(computer, ball)
    intersection_check(player, ball)
    intersection_check(top, ball)
    intersection_check(bottom, ball)
    intersection_check(left, ball)
    intersection_check(right, ball)
    player.draw()
    computer.draw()
    top.draw()
    bottom.draw()
    left.draw()
    right.draw()
    ball.draw()


pyglet.clock.schedule_interval(update, 0.01)
pyglet.app.run()
