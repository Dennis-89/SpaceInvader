import pygame
import random
from pygame import mixer
from pathlib import Path


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

PLAYER_SPEED = 0.4
BULLET_SPEED = 0.8

NUMBER_OF_ENEMY = 10
ENEMY_SPEED = 0.3
ENEMY_STEP_CLOSER = 40


def clear_screen(screen, background):
    screen.fill((0, 0, 0))
    screen.blit(background, (0, 0))


def is_collision(enemy_x, enrmy_y, bullet_x, bullet_y):
    return ((bullet_x - enemy_x) ** 2 + (bullet_y - enrmy_y) ** 2) ** 0.5 < 27


def fire_bullet(screen, bullet_image, position):
    screen.blit(bullet_image, position)


def move_enemy(screen, enemy_image, position):
    screen.blit(enemy_image, position)


def move_player(screen, player_image, position):
    screen.blit(player_image, position)


def process_user_input(
    pygame,
    event,
    player_x_change,
    player_x_position,
    bullet_is_ready,
    bullet_y_position,
    bullet_image,
    screen,
):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
            player_x_change -= PLAYER_SPEED
        elif event.key == pygame.K_RIGHT:
            player_x_change += PLAYER_SPEED
        elif event.key == pygame.K_SPACE and bullet_is_ready:
            fire_bullet(screen, bullet_image, (player_x_position, bullet_y_position))
            bullet_is_ready = False
            shut_sound = mixer.Sound("laser.wav")
            shut_sound.play()
    if event.type == pygame.KEYUP:
        if event.key == pygame.K_LEFT:
            player_x_change += PLAYER_SPEED
        elif event.key == pygame.K_RIGHT:
            player_x_change -= PLAYER_SPEED
    return player_x_change, bullet_is_ready, player_x_position


def set_new_enemy_position(enemy_x_position, enemy_y_position, right_way):
    if right_way:
        enemy_x_position += ENEMY_SPEED
    else:
        enemy_x_position -= ENEMY_SPEED
    if enemy_x_position <= 0:
        return 0, enemy_y_position + ENEMY_STEP_CLOSER, True
    elif enemy_x_position >= WIDTH - IMAGE_SIZE_ENEMY[0]:
        return WIDTH - IMAGE_SIZE_ENEMY[0], enemy_y_position + ENEMY_STEP_CLOSER, False
    if enemy_y_position > 600:
        return enemy_x_position, 50, True
    return enemy_x_position, enemy_y_position, right_way


def set_new_player_position(player_x_position, player_x_change):
    player_x_position += player_x_change
    if player_x_position <= 0:
        return 0
    elif player_x_position >= WIDTH - IMAGE_SIZE_PLAYER[0]:
        return WIDTH - IMAGE_SIZE_PLAYER[0]
    return player_x_position


def show_score(font, score_value, screen, position):
    score = font.render(f"Score : {score_value}", True, (255, 255, 255))
    screen.blit(score, position)


def main():
    pygame.init()
    pygame.display.set_caption("Space Invader")
    screen = pygame.display.set_mode(SCREEN_SIZE)
    background = pygame.image.load(BACKGROUND_IMAGE)
    background = pygame.transform.scale(background, SCREEN_SIZE)
    pygame.display.set_icon(pygame.image.load(UFO_IMAGE))
    player_image = pygame.transform.scale(
        pygame.image.load(PLAYER_IMAGE), IMAGE_SIZE_PLAYER
    )
    player_x_change = 0
    player_x_position = START_POSITION_PLAYER_X
    player_y_position = START_POSITION_PLAYER_Y
    enemy_image = pygame.transform.scale(
        pygame.image.load(ENEMY_IMAGE), IMAGE_SIZE_ENEMY
    )
    enemy_positions = [
        (random.randint(0, WIDTH - IMAGE_SIZE_ENEMY[0]), random.randint(50, 150), True)
        for _ in range(NUMBER_OF_ENEMY)
    ]
    bullet_image = pygame.transform.scale(
        pygame.image.load(BULLET_IMAGE), IMAGE_SIZE_BULLET
    )
    bullet_x_position = 0
    bullet_y_position = player_y_position
    bullet_is_ready = True
    score_value = 0
    font = pygame.font.Font("freesansbold.ttf", 32)
    is_running = True

    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            player_x_change, bullet_is_ready, bullet_x_position = process_user_input(
                pygame,
                event,
                player_x_change,
                player_x_position,
                bullet_is_ready,
                bullet_y_position,
                bullet_image,
                screen,
            )
        clear_screen(screen, background)
        player_x_position = set_new_player_position(player_x_position, player_x_change)
        move_player(screen, player_image, (player_x_position, player_y_position))
        new_positions = []
        for enemy_x_position, enemy_y_position, right_way in enemy_positions:
            enemy_x_position, enemy_y_position, right_way = set_new_enemy_position(
                enemy_x_position, enemy_y_position, right_way
            )

            if is_collision(
                enemy_x_position, enemy_y_position, bullet_x_position, bullet_y_position
            ):
                bullet_y_position = 480
                bullet_is_ready = True
                score_value += 1
                enemy_x_position = random.randint(0, WIDTH - IMAGE_SIZE_ENEMY[0])
                enemy_y_position = random.randint(50, 150)
                ex_sound = mixer.Sound("explosion.wav")
                ex_sound.play()
            move_enemy(screen, enemy_image, (enemy_x_position, enemy_y_position))
            new_positions.append((enemy_x_position, enemy_y_position, right_way))
        enemy_positions = new_positions

        if not bullet_is_ready:
            fire_bullet(screen, bullet_image, (bullet_x_position, bullet_y_position))
            bullet_y_position -= BULLET_SPEED
        if bullet_y_position < -50:
            bullet_is_ready = True
            bullet_y_position = player_y_position
        show_score(font, score_value, screen, (SCORE_TEXT_X, SCORE_TEXT_Y))
        pygame.display.update()


if __name__ == "__main__":
    main()
