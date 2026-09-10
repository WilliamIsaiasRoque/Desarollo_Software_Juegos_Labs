import math
import random

import pygame
from pygame import mixer

# Inicializar pygame
pygame.init()

# Crear la pantalla
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Reloj (fija la velocidad del juego a los FPS en vez de depender del hardware)
clock = pygame.time.Clock()
FPS = 60

# Fondos por nivel (el índice se elige según el puntaje, ver LEVEL_THRESHOLDS)
backgrounds = [
    pygame.image.load('lvl1.jpg'),
    pygame.image.load('lvl2.jpg'),
    pygame.image.load('lvl3.jpg'),
]
LEVEL_THRESHOLDS = [0, 5, 10]  # puntaje mínimo para entrar a cada nivel
LEVEL_SPEED_MULTIPLIERS = [1.0, 1.6, 2.2]  # velocidad de enemigos por nivel

# Sonido
mixer.music.load("background.wav")
mixer.music.play(-1)

# Título e ícono
pygame.display.set_caption("Space Invader")
icon = pygame.image.load('ufo.png')
pygame.display.set_icon(icon)

# Tamaños de renderizado fijos: los archivos de imagen pueden venir en
# cualquier resolución (512x512, 840x1127, etc.), pero en el juego siempre
# se dibujan a este tamaño, sin importar el tamaño real del archivo
PLAYER_SIZE = (64, 64)
ENEMY_SIZE = (64, 64)
BULLET_SIZE = (32, 32)

# Jugador
playerImg = pygame.transform.scale(pygame.image.load('player.png'), PLAYER_SIZE)
PLAYER_X_MAX = SCREEN_WIDTH - playerImg.get_width()  # antes fijo en 736 (ancho de pantalla viejo - sprite); no llegaba al borde derecho al cambiar el tamaño de la ventana
playerX = PLAYER_X_MAX // 2
playerY = SCREEN_HEIGHT - 230  # antes -200: un poco más arriba
PLAYER_Y_MIN = playerY  # no puede subir más de su altura actual
PLAYER_Y_MAX = playerY + 100  # "barrera invisible" hasta donde puede bajar
playerX_change = 0
playerY_change = 0
PLAYER_SPEED = 6  # píxeles por frame a 60 FPS (ajustado tras agregar clock.tick)

# Estado independiente por tecla (arregla el bug donde soltar una tecla de
# dirección cancelaba el movimiento aunque la tecla opuesta siguiera presionada)
left_pressed = False
right_pressed = False
up_pressed = False
down_pressed = False
space_pressed = False

# Enemigo
# Imágenes por nivel (el índice es el mismo current_level usado para el fondo)
enemyImages = [
    pygame.transform.scale(pygame.image.load('enemy1.png'), ENEMY_SIZE),
    pygame.transform.scale(pygame.image.load('enemy2.png'), ENEMY_SIZE),
    pygame.transform.scale(pygame.image.load('enemy3.png'), ENEMY_SIZE),
]
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 6
ENEMY_SPEED = 3  # antes 1: quedaba muy lento tras limitar los FPS a 60
ENEMY_X_MAX = SCREEN_WIDTH - ENEMY_SIZE[0]
GAME_OVER_LINE = playerY - 140  # si un enemigo cruza esta línea, termina el juego

for i in range(num_of_enemies):
    enemyX.append(random.randint(0, ENEMY_X_MAX))
    enemyY.append(random.randint(0, 150))
    enemyX_change.append(1)  # dirección: 1 = derecha, -1 = izquierda (la velocidad se aplica aparte, ver LEVEL_SPEED_MULTIPLIERS)
    enemyY_change.append(40)

# Bala

# Ready - La bala no es visible en pantalla
# Fire - La bala está actualmente en movimiento

bulletImg = pygame.transform.scale(pygame.image.load('bullet.png'), BULLET_SIZE)
BULLET_RESET_Y = playerY - 100  # posición de "lista para disparar", relativa a la nave (antes fija en 480)
bulletX = 0
bulletY = BULLET_RESET_Y
bulletX_change = 0
bulletY_change = 18  # antes 10: quedaba muy lenta tras limitar los FPS a 60
bullet_state = "ready"

# Bala enemiga: imagen propia, igual para los 3 niveles
enemyBulletImg = pygame.transform.scale(pygame.image.load('bulletenemy.png'), BULLET_SIZE)
enemyBulletX = 0
enemyBulletY = 0
ENEMY_BULLET_SPEED = 8
enemy_bullet_state = "ready"

# Puntaje

score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)

textX = 10
testY = 10

# Game Over
over_font = pygame.font.Font('freesansbold.ttf', 64)
game_over = False

# Menú inicial y pausa
menu_font = pygame.font.Font('freesansbold.ttf', 64)
game_started = False
paused = False


def show_score(x, y):
    score = font.render("Score : " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))


def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 255, 255))
    over_rect = over_text.get_rect(center=(SCREEN_WIDTH // 2, 280))
    screen.blit(over_text, over_rect)

    restart_text = font.render("Press R to restart", True, (255, 255, 255))
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, 350))
    screen.blit(restart_text, restart_rect)


def start_menu():
    title_text = menu_font.render("SPACE INVADER", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 280))
    screen.blit(title_text, title_rect)

    start_text = font.render("Presiona ESPACIO para comenzar", True, (255, 255, 255))
    start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, 360))
    screen.blit(start_text, start_rect)

    pause_hint_text = font.render("Presiona P para pausar el juego", True, (255, 255, 255))
    pause_hint_rect = pause_hint_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
    screen.blit(pause_hint_text, pause_hint_rect)


def pause_text():
    paused_text = over_font.render("PAUSA", True, (255, 255, 255))
    paused_rect = paused_text.get_rect(center=(SCREEN_WIDTH // 2, 280))
    screen.blit(paused_text, paused_rect)

    resume_text = font.render("Presiona P para continuar", True, (255, 255, 255))
    resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, 350))
    screen.blit(resume_text, resume_rect)


def reset_game():
    global playerX, playerY, bulletY, bullet_state, enemy_bullet_state, score_value, game_over, paused
    playerX = PLAYER_X_MAX // 2
    playerY = PLAYER_Y_MIN
    bulletY = BULLET_RESET_Y
    bullet_state = "ready"
    enemy_bullet_state = "ready"
    score_value = 0
    game_over = False
    paused = False
    for i in range(num_of_enemies):
        enemyX[i] = random.randint(0, ENEMY_X_MAX)
        enemyY[i] = random.randint(0, 150)
        enemyX_change[i] = 1


def player(x, y):
    screen.blit(playerImg, (x, y))


def enemy(x, y):
    screen.blit(enemyImages[current_level], (x, y))


def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bulletImg, (x + 16, y + 10))


def fire_enemy_bullet(x, y):
    global enemy_bullet_state
    enemy_bullet_state = "fire"
    screen.blit(enemyBulletImg, (x + 16, y + 10))


def isCollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt(math.pow(enemyX - bulletX, 2) + (math.pow(enemyY - bulletY, 2)))
    if distance < 27:
        return True
    else:
        return False


# Bucle del juego
running = True
while running:

    # Nivel actual según el puntaje: recorre los umbrales de mayor a menor
    # y se queda con el primero que el puntaje ya alcanzó
    current_level = 0
    for level_index in range(len(LEVEL_THRESHOLDS) - 1, -1, -1):
        if score_value >= LEVEL_THRESHOLDS[level_index]:
            current_level = level_index
            break

    # RGB = Rojo, Verde, Azul
    screen.fill((0, 0, 0))
    # Imagen de fondo (según el nivel actual)
    screen.blit(backgrounds[current_level], (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # si se presiona una tecla, revisar si es izquierda, derecha, espacio o R
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                left_pressed = True
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                right_pressed = True
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                up_pressed = True
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                down_pressed = True
            if event.key == pygame.K_SPACE:
                space_pressed = True
                if not game_started:
                    game_started = True
            if event.key == pygame.K_r and game_over:
                reset_game()
            if event.key == pygame.K_p and game_started and not game_over:
                paused = not paused

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                left_pressed = False
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                right_pressed = False
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                up_pressed = False
            if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                down_pressed = False
            if event.key == pygame.K_SPACE:
                space_pressed = False

    # 5 = 5 + -0.1 -> 5 = 5 - 0.1
    # 5 = 5 + 0.1

    if not game_started:
        start_menu()
    elif game_over:
        game_over_text()
    elif paused:
        pause_text()
    else:
        # Disparar automáticamente cada frame mientras se mantiene la barra
        # espaciadora presionada, tan pronto la bala anterior vuelve a estar
        # lista (en vez de necesitar una nueva pulsación de tecla)
        if space_pressed and bullet_state == "ready":
            bulletSound = mixer.Sound("laser.wav")
            bulletSound.play()
            bulletX = playerX
            bulletY = playerY - 40  # nace justo encima de la nave, sigue su altura actual
            fire_bullet(bulletX, bulletY)

        playerX_change = (int(right_pressed) - int(left_pressed)) * PLAYER_SPEED
        playerX += playerX_change
        if playerX <= 0:
            playerX = 0
        elif playerX >= PLAYER_X_MAX:
            playerX = PLAYER_X_MAX

        playerY_change = (int(down_pressed) - int(up_pressed)) * PLAYER_SPEED
        playerY += playerY_change
        if playerY <= PLAYER_Y_MIN:
            playerY = PLAYER_Y_MIN
        elif playerY >= PLAYER_Y_MAX:
            playerY = PLAYER_Y_MAX

        # Movimiento de los enemigos
        for i in range(num_of_enemies):

            # Game Over: detener el juego en vez de solo ocultar los enemigos
            if enemyY[i] > GAME_OVER_LINE:
                game_over = True
                break

            effective_enemy_speed = ENEMY_SPEED * LEVEL_SPEED_MULTIPLIERS[current_level]
            enemyX[i] += int(enemyX_change[i] * effective_enemy_speed)
            if enemyX[i] <= 0:
                enemyX_change[i] = 1
                enemyY[i] += enemyY_change[i]
            elif enemyX[i] >= ENEMY_X_MAX:
                enemyX_change[i] = -1
                enemyY[i] += enemyY_change[i]

            # Colisión
            collision = isCollision(enemyX[i], enemyY[i], bulletX, bulletY)
            if collision:
                explosionSound = mixer.Sound("explosion.wav")
                explosionSound.play()
                bulletY = BULLET_RESET_Y
                bullet_state = "ready"
                score_value += 1
                enemyX[i] = random.randint(0, ENEMY_X_MAX)
                enemyY[i] = random.randint(50, 150)

            enemy(enemyX[i], enemyY[i])

        # Movimiento de la bala
        if bulletY <= 0:
            bulletY = BULLET_RESET_Y
            bullet_state = "ready"

        if bullet_state == "fire":
            fire_bullet(bulletX, bulletY)
            bulletY -= bulletY_change

        # Disparo de los enemigos: dispara uno al azar; cuando su bala termina
        # el recorrido, vuelve a "ready" y se elige otro enemigo al azar
        if enemy_bullet_state == "ready":
            shooting_enemy = random.randint(0, num_of_enemies - 1)
            enemyBulletX = enemyX[shooting_enemy]
            enemyBulletY = enemyY[shooting_enemy]
            fire_enemy_bullet(enemyBulletX, enemyBulletY)

        if enemyBulletY >= SCREEN_HEIGHT:
            enemy_bullet_state = "ready"

        if enemy_bullet_state == "fire":
            fire_enemy_bullet(enemyBulletX, enemyBulletY)
            effective_enemy_bullet_speed = ENEMY_BULLET_SPEED * LEVEL_SPEED_MULTIPLIERS[current_level]
            enemyBulletY += int(effective_enemy_bullet_speed)

            # Colisión de la bala enemiga contra el jugador
            hit_player = isCollision(playerX, playerY, enemyBulletX, enemyBulletY)
            if hit_player:
                explosionSound = mixer.Sound("explosion.wav")
                explosionSound.play()
                game_over = True

    player(playerX, playerY)
    show_score(textX, testY)
    pygame.display.update()
    clock.tick(FPS)
