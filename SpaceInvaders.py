import pygame
import random
from pygame import mixer
from pathlib import Path
from attr import attrib, attrs


WIDTH = 800
HIGH = 600
SCREEN_SIZE = (WIDTH, HIGH)
BACKGROUND_IMAGE = Path(__file__).parent / "space.jpg"
UFO_IMAGE = Path(__file__).parent / "ufo.png"
ENEMY_IMAGE = Path(__file__).parent / "monster.png"
IMAGE_SIZE_ENEMY = (63, 63)
PLAYER_IMAGE = Path(__file__).parent / "Player.png"
IMAGE_SIZE_PLAYER = (63, 63)
BULLET_IMAGE = Path(__file__).parent / "rocket.png"
IMAGE_SIZE_BULLET = (64, 64)

SCORE_TEXT_X = 10
SCORE_TEXT_Y = 10

START_POSITION_PLAYER_X = 370
START_POSITION_PLAYER_Y = HIGH - 120

PLAYER_SPEED = 1
BULLET_SPEED = 0.8

NUMBER_OF_ENEMY = 10
ENEMY_SPEED = 0.3
ENEMY_STEP_CLOSER = 40


@attrs(frozen=False)
class Figure:
    x_position = attrib(default=0)
    y_position = attrib(default=0)
    move_in_x = attrib(default=0)
    move_in_y = attrib(default=0)
    default_direction = attrib(default="+")

    def __attrs_post_init__(self):
        self.direction = {"+": self.move_in_x, "-": -1 * self.move_in_x}

    def calculate_next_position(self, direction=None):
        if direction is None:
            direction = self.default_direction
        self.x_position += self.direction[direction]
        if self.x_position < 0 or self.x_position > WIDTH - IMAGE_SIZE_PLAYER[0]:
            self.x_position = WIDTH - IMAGE_SIZE_PLAYER[0] if direction == "+" else 0
            if self.move_in_y != 0:
                self._change_y_position()

    def _change_y_position(self):
        if self.y_position > HIGH:
            self.y_position = 50
        else:
            self.y_position += ENEMY_STEP_CLOSER
        self.default_direction = "+" if self.default_direction == "-" else "-"


@attrs(frozen=False)
class Bullet:
    x_position = attrib(default=0)
    y_position = attrib(default=START_POSITION_PLAYER_Y)
    is_ready = attrib(default=True)

    def change_y_position(self):
        self.y_position -= BULLET_SPEED


def clear_screen(screen, background):
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))


def is_collision(enemy, bullet):
    if bullet.is_ready:
        return False
    return (
        abs(bullet.x_position - enemy.x_position) < 27 and abs(bullet.y_position - enemy.y_position) < 27
    )


def fire_bullet(screen, bullet_image, position):
    screen.blit(bullet_image, position)


def move_figure(screen, image, position):
    screen.blit(image, position)


def process_user_input(pygame, bullet, player, keys):
    if keys[pygame.K_LEFT]:
        player.calculate_next_position("-")
    elif keys[pygame.K_RIGHT]:
        player.calculate_next_position("+")
    elif keys[pygame.K_SPACE] and bullet.is_ready:
        shut_sound = mixer.Sound("laser.wav")
        shut_sound.play()
        bullet.x_position = player.x_position
        bullet.is_ready = False
    return bullet


def show_score(font, score_value, screen, position):
    score = font.render(f"Score : {score_value}", True, (255, 255, 255))
    screen.blit(score, position)


def main():
    pygame.init()
    pygame.display.set_caption("Space Invader")
    screen = pygame.display.set_mode(SCREEN_SIZE)
    background = pygame.image.load(BACKGROUND_IMAGE)
    pygame.display.set_icon(pygame.image.load(UFO_IMAGE))
    player_image = pygame.transform.scale(
        pygame.image.load(PLAYER_IMAGE), IMAGE_SIZE_PLAYER
    )
    player = Figure(START_POSITION_PLAYER_X, START_POSITION_PLAYER_Y, PLAYER_SPEED)
    enemies = [
        Figure(
            random.randint(0, WIDTH - IMAGE_SIZE_ENEMY[0]),
            random.randint(50, 150),
            ENEMY_SPEED,
            ENEMY_STEP_CLOSER,
        )
        for _ in range(NUMBER_OF_ENEMY)
    ]
    enemy_image = pygame.transform.scale(
        pygame.image.load(ENEMY_IMAGE), IMAGE_SIZE_ENEMY
    )
    bullet_image = pygame.transform.scale(
        pygame.image.load(BULLET_IMAGE), IMAGE_SIZE_BULLET
    )
    score_value = 0
    font = pygame.font.Font("freesansbold.ttf", 32)
    is_running = True
    bullet = Bullet()
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
        keys = pygame.key.get_pressed()
        bullet = process_user_input(pygame, bullet, player, keys)
        clear_screen(screen, background)
        move_figure(screen, player_image, (player.x_position, player.y_position))
        for enemy in enemies:
            enemy.calculate_next_position()
            if is_collision(enemy, bullet):
                bullet = Bullet()
                score_value += 1
                enemy.x_position = random.randint(0, WIDTH - IMAGE_SIZE_ENEMY[0])
                enemy.y_position = random.randint(50, 150)
                ex_sound = mixer.Sound("explosion.wav")
                ex_sound.play()
            move_figure(screen, enemy_image, (enemy.x_position, enemy.y_position))

        if not bullet.is_ready:
            fire_bullet(screen, bullet_image, (bullet.x_position, bullet.y_position))
            bullet.change_y_position()
        if bullet.y_position < -50:
            bullet = Bullet()
        show_score(font, score_value, screen, (SCORE_TEXT_X, SCORE_TEXT_Y))
        pygame.display.update()


if __name__ == "__main__":
    main()
