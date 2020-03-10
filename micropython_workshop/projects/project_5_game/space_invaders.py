"""
This script implements a (simple) game of space invaders using an attached
I2C OLED screen and a couple of buttons
"""

from machine import Pin, I2C
import ssd1306
import time

import sprites

i2c = I2C(-1, scl=Pin(2), sda=Pin(0))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)
left_button = Pin(5, Pin.IN)
right_button = Pin(4, Pin.IN)
fire_button = Pin(14, Pin.IN)
missles = []
enemies = []
score = 0
high_score = 0


class Missle:
    """Keeps track of an on-screen missle"""

    def __init__(self, x, y):
        """Save our starting state"""
        self.x = x
        self.y = y
        self.active = True

    def move(self):
        """If we move above the top of the screen, mark
        ourselves as not active. The game loop should
        cleanup any non-active missles.
        """

        self.y -= 5
        if self.y < 0:
            self.active = False

    def draw(self):
        """Draw ourselves at our current posistion"""
        for y_offset in range(5):
            oled.pixel(self.x, self.y - y_offset, 1)


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.active = True
        self.sprites =  [sprites.ENEMY_SPRITE1, sprites.ENEMY_SPRITE2]
        self.current_sprite = 0
        self.sprite_changed = time.ticks_ms()

    def move(self):
        pass

    def draw(self):
        now = time.ticks_ms()
        if now - self.sprite_changed > 1000:
            self.current_sprite += 1
            self.current_sprite %= len(self.sprites)
            self.sprite_changed = now
        oled.blit(self.sprites[self.current_sprite], self.x, self.y)


class Ship:
    """Keep track of the player's ship"""

    def __init__(self, x, y):
        """Save our initial state"""
        self.x = x
        self.y = y
        self.last_fired = time.ticks_ms()

    def move(self):
        """Move left or right depending on which button is pressed"""

        if left_button.value():
            self.x -= 3
        if right_button.value():
            self.x += 3
        if self.x > 119:
            self.x = 119
        if self.x < 9:
            self.x = 9

    def draw(self):
        """Draw the pixels of our ship"""

        oled.blit(sprites.SHIP_SPRITE, self.x - 8, self.y - 5)

    def fire(self):
        """If the fire button is pressed and the cooldown time has
        passed, then generate a new missle object at our current position
        """

        now = time.ticks_ms()
        if fire_button.value() and now - self.last_fired > 200:
            self.last_fired = now
            missles.append(Missle(self.x, self.y - 10))


def update_missles():
    """Remove any non-active missles and move the rest"""

    global missles
    missles = [m for m in missles if m.active]
    for missle in missles:
        missle.move()
        missle.draw()

def update_enemies():
    """Remove any destroyed enemies and move the rest"""

    global enemies
    enemies = [e for e in enemies if e.active]
    for enemy in enemies:
        enemy.move()
        enemy.draw()

def update_score():
    oled.text("Score:%s" % score, 0, 0)
    hi_text = "Hi:%s" % max(high_score, score)
    oled.text(hi_text, 128 - len(hi_text) * 10, 0)

def game_loop(ship):
    """Drive the main game loop"""

    oled.fill(0)
    ship.fire()
    update_missles()
    update_enemies()
    ship.move()
    ship.draw()
    update_score()
    oled.show()

try:
    ship = Ship(64, 64)
    for y in range(12, 36, 12):
        for x in range(10, 118, 16):
            enemies.append(Enemy(x, y))
    while True:
        game_loop(ship)
except KeyboardInterrupt:
    pass
