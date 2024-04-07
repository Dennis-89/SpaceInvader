import random
from itertools import product
from pathlib import Path

import pygame
from attr import define, field
from pygame import mixer
from pygame.sprite import Group, Sprite
from pygame.time import Clock, set_timer

WIDTH = 800
HIGH = 600
SCREEN_SIZE = (WIDTH, HIGH)

FILES_PATH = Path(__file__).parent

BACKGROUND_IMAGE = FILES_PATH / "space.jpg"
ENEMY_IMAGE = FILES_PATH / "monster.png"
IMAGE_SIZE_ENEMY = (63, 63)
PLAYER_IMAGE = FILES_PATH / "Player.png"
IMAGE_SIZE_PLAYER = (63, 63)
BULLET_IMAGE = FILES_PATH / "rocket.png"
IMAGE_SIZE_BULLET = (64, 64)

SHOOT_SOUND = FILES_PATH / "laser.wav"

SCORE_TEXT_X = 10
SCORE_TEXT_Y = 10

START_POSITION_PLAYER_X = 370
START_POSITION_Y = HIGH - 120

PLAYER_SPEED = 5

NUMBER_OF_ENEMY = 30
ENEMY_SPEED = 1
ENEMY_Y_STEP = 40

NUMBER_OF_BULLETS = 100
BULLET_SPEED = 5


class Figure(Sprite):
    def __init__(self, rect, image):
        Sprite.__init__(self)
        self.rect = rect
        self.image = image

    @classmethod
    def new(cls, x, y, image_size, image):
        return cls(pygame.Rect(x, y, *image_size), image)

    def update(self, x, y=0):
        self.rect.move_ip(x, 0)
        if y == 0:
            if self.rect.x <= 0:
                self.rect.x = 0
            elif self.rect.x >= WIDTH - IMAGE_SIZE_ENEMY[0]:
                self.rect.x = WIDTH - IMAGE_SIZE_ENEMY[0]
        elif self.rect.x >= WIDTH:
            self.rect.x = 0
            self.rect.y += y
        elif self.rect.y > START_POSITION_Y - IMAGE_SIZE_ENEMY[0]:
            self.rect.y = random.randint(50, 150)


class Bullet(Sprite):
    def __init__(self, rect, image):
        Sprite.__init__(self)
        self.rect = rect
        self.image = image
        self.is_active = False

    @classmethod
    def new(cls, x, y, image_size, image):
        return cls(pygame.Rect(x, y, *image_size), image)

    def update(self):
        if self.is_active:
            if self.rect.y == HIGH + IMAGE_SIZE_BULLET[0]:
                self.rect.y = START_POSITION_Y
            self.rect.y -= BULLET_SPEED
            if self.rect.y < 0:
                self.is_active = False
                self.rect.y = HIGH + IMAGE_SIZE_BULLET[0]


@define
class Game:
    screen = field()
    background = field()
    players = field()
    enemies = field()
    bullets = field()
    font = field()
    fire_event = field()
    score = field(default=0)
    gun_is_ready = field(default=True)

    def run(self):
        clock = Clock()
        game_on = True
        while game_on:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_on = False
                if event.type == self.fire_event:
                    self.gun_is_ready = True
                    set_timer(self.fire_event, 0)
            keys = pygame.key.get_pressed()
            self.process_user_input(keys)
            for bullet, enemy in product(self.bullets, self.enemies):
                if is_collided_with(bullet, enemy) and bullet.is_active:
                    bullet.is_active = False
                    bullet.rect.y = HIGH + IMAGE_SIZE_BULLET[0]
                    enemy.rect.x = random.randint(0, WIDTH - IMAGE_SIZE_ENEMY[0])
                    enemy.rect.y = random.randint(50, 150)
                    self.score += 1
                    break
            self.screen.blit(self.background, (0, 0))
            self.screen.blit(
                self.font.render(f"Score : {self.score}", True, (255, 255, 255)),
                (SCORE_TEXT_X, SCORE_TEXT_Y),
            )
            self.players.draw(self.screen)
            self.enemies.update(ENEMY_SPEED, ENEMY_Y_STEP)
            self.enemies.draw(self.screen)
            self.bullets.update()
            self.bullets.draw(self.screen)
            pygame.display.update()
            clock.tick(100)

    def process_user_input(self, keys):
        if keys[pygame.K_LEFT]:
            self.players.update(-PLAYER_SPEED)
        elif keys[pygame.K_RIGHT]:
            self.players.update(PLAYER_SPEED)
        elif keys[pygame.K_SPACE] and self.gun_is_ready:
            self.gun_is_ready = False
            mixer.Sound(SHOOT_SOUND).play()
            for bullet in self.bullets:
                if not bullet.is_active:
                    bullet.is_active = True
                    for player in self.players:
                        bullet.rect.x = player.rect.x
                    break
            set_timer(self.fire_event, 100)


def is_collided_with(bullet, enemy):
    if bullet.is_active:
        return pygame.sprite.collide_rect(bullet, enemy)


def main():
    pygame.init()
    pygame.display.set_caption("Space Invader")
    screen = pygame.display.set_mode(SCREEN_SIZE)
    background = pygame.image.load(BACKGROUND_IMAGE)
    player_image = pygame.transform.scale(
        pygame.image.load(PLAYER_IMAGE), IMAGE_SIZE_PLAYER
    )
    enemy_image = pygame.transform.scale(
        pygame.image.load(ENEMY_IMAGE), IMAGE_SIZE_ENEMY
    )
    bullet_image = pygame.transform.scale(
        pygame.image.load(BULLET_IMAGE), IMAGE_SIZE_BULLET
    )
    player = Group()
    player.add(
        Figure.new(
            START_POSITION_PLAYER_X,
            START_POSITION_Y,
            IMAGE_SIZE_PLAYER,
            player_image,
        )
    )
    enemies = Group()
    enemies.add(
        *[
            Figure.new(
                random.randint(0, WIDTH - IMAGE_SIZE_ENEMY[0]),
                random.randint(50, 150),
                IMAGE_SIZE_ENEMY,
                enemy_image,
            )
            for _ in range(NUMBER_OF_ENEMY)
        ]
    )
    bullets = pygame.sprite.Group()
    bullets.add(
        *[
            Bullet.new(
                -IMAGE_SIZE_BULLET[0],
                START_POSITION_Y,
                IMAGE_SIZE_BULLET,
                bullet_image,
            )
            for _ in range(NUMBER_OF_BULLETS)
        ]
    )

    font = pygame.font.Font("freesansbold.ttf", 32)

    game = Game(
        screen, background, player, enemies, bullets, font, pygame.USEREVENT + 1
    )
    game.run()


if __name__ == "__main__":
    main()
