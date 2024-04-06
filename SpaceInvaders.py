import pygame
import random
from pygame import mixer
from pathlib import Path
from attr import define, field
from itertools import product

WIDTH = 800
HIGH = 600
SCREEN_SIZE = (WIDTH, HIGH)
BACKGROUND_IMAGE = Path(__file__).parent / "space.jpg"
ENEMY_IMAGE = Path(__file__).parent / "monster.png"
IMAGE_SIZE_ENEMY = (63, 63)
PLAYER_IMAGE = Path(__file__).parent / "Player.png"
IMAGE_SIZE_PLAYER = (63, 63)
BULLET_IMAGE = Path(__file__).parent / "rocket.png"
IMAGE_SIZE_BULLET = (64, 64)

SCORE_TEXT_X = 10
SCORE_TEXT_Y = 10

START_POSITION_PLAYER_X = 370
START_POSITION_Y = HIGH - 120

PLAYER_SPEED = 1
BULLET_SPEED = 0.2

NUMBER_OF_ENEMY = 10
ENEMY_SPEED = 0.3
ENEMY_Y_STEP = 40
MAX_DISTANCE_BULLET = 28
MAX_ENEMIES = 80
MAX_BULLETS = 1


@define
class CollisionDetector:
    x = field()
    y = field()

    def __add__(self, other):
        return CollisionDetector(abs(self.x - other.x), abs(self.y - other.y))

    def __call__(self):
        return self.x < MAX_DISTANCE_BULLET and self.y < MAX_DISTANCE_BULLET


@define
class Figure(CollisionDetector):
    direction = field()
    default_direction = field(default="+")
    y_direction_blocked = field(default=True)

    @classmethod
    def new(cls, x, y, move_in_x, blocked):
        return cls(x, y, {"+": move_in_x, "-": -move_in_x}, y_direction_blocked=blocked)

    def calculate_next_position(self, direction=None):
        if direction is None:
            direction = self.default_direction
        self.x += self.direction[direction]
        if self.x < 0 or self.x > WIDTH - IMAGE_SIZE_PLAYER[0]:
            self.x = WIDTH - IMAGE_SIZE_PLAYER[0] if direction == "+" else 0
            if not self.y_direction_blocked:
                self._change_y_position()

    def _change_y_position(self):
        if self.y > HIGH:
            self.y = 50
        else:
            self.y += ENEMY_Y_STEP
        self.default_direction = "+" if self.default_direction == "-" else "-"


@define
class Bullet(CollisionDetector):
    is_active = field(default=False)

    def change_y_position(self):
        self.y -= BULLET_SPEED


@define
class Game:
    screen = field()
    background = field()
    player_image = field()
    enemy_image = field()
    bullet_image = field()
    player = field()
    bullets = field()
    enemies = field()
    font = field()
    game_on = field(default=True)
    is_gun_loaded = field(default=True)
    score = field(default=0)

    def run(self):
        while self.game_on:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_on = False
            keys = pygame.key.get_pressed()
            self.process_user_input(keys)
            self.clear_screen()
            self.move_figure(self.player_image, (self.player.x, self.player.y))
            for enemy, bullet in product(self.enemies, self.bullets):
                enemy.calculate_next_position()
                if (enemy + bullet)() and bullet.is_active:
                    bullet.y = self.player.y
                    bullet.is_active = False
                    self.score += 1
                    enemy.x = random.randint(0, WIDTH - IMAGE_SIZE_ENEMY[0])
                    enemy.y = random.randint(50, 150)
                    ex_sound = mixer.Sound("explosion.wav")
                    ex_sound.play()
                    if len(self.enemies) < MAX_ENEMIES:
                        self.enemies.append(
                            Figure.new(
                                random.randint(0, WIDTH - IMAGE_SIZE_ENEMY[0]),
                                random.randint(50, 150),
                                ENEMY_SPEED,
                                False,
                            )
                        )
                self.move_figure(self.enemy_image, (enemy.x, enemy.y))
                if bullet.is_active:
                    self.move_figure(self.bullet_image, (bullet.x, bullet.y))
                    bullet.change_y_position()
                    if bullet.y < -50:
                        bullet.y = self.player.y
                        bullet.x = self.player.x
                        bullet.is_active = False
            self.show_score((SCORE_TEXT_X, SCORE_TEXT_Y))
            pygame.display.update()

    def process_user_input(self, keys):
        if keys[pygame.K_LEFT]:
            self.player.calculate_next_position("-")
        elif keys[pygame.K_RIGHT]:
            self.player.calculate_next_position("+")
        elif keys[pygame.K_SPACE]:
            for bullet in self.bullets:
                if not bullet.is_active:
                    mixer.Sound("laser.wav").play()
                    bullet.x = self.player.x
                    bullet.is_active = True

    def clear_screen(self):
        self.screen.blit(self.background, (0, 0))

    def move_figure(self, image, position):
        self.screen.blit(image, position)

    def show_score(self, position):
        self.screen.blit(
            self.font.render(f"Score : {self.score}", True, (255, 255, 255)), position
        )


def main():
    pygame.init()
    pygame.display.set_caption("Space Invader")
    screen = pygame.display.set_mode(SCREEN_SIZE)
    background = pygame.image.load(BACKGROUND_IMAGE)
    player_image = pygame.transform.scale(
        pygame.image.load(PLAYER_IMAGE), IMAGE_SIZE_PLAYER
    )
    player = Figure.new(START_POSITION_PLAYER_X, START_POSITION_Y, PLAYER_SPEED, True)
    enemies = [
        Figure.new(
            random.randint(0, WIDTH - IMAGE_SIZE_ENEMY[0]),
            random.randint(50, 150),
            ENEMY_SPEED,
            False,
        )
        for _ in range(NUMBER_OF_ENEMY)
    ]
    bullets = [
        Bullet(x=0, y=START_POSITION_Y, is_active=False) for _ in range(MAX_BULLETS)
    ]
    enemy_image = pygame.transform.scale(
        pygame.image.load(ENEMY_IMAGE), IMAGE_SIZE_ENEMY
    )
    bullet_image = pygame.transform.scale(
        pygame.image.load(BULLET_IMAGE), IMAGE_SIZE_BULLET
    )
    font = pygame.font.Font("freesansbold.ttf", 32)

    game = Game(
        screen,
        background,
        player_image,
        enemy_image,
        bullet_image,
        player,
        bullets,
        enemies,
        font,
    )
    game.run()


if __name__ == "__main__":
    main()
