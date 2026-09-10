import math
import random

import pygame
from pygame import mixer

# Inicializar pygame
pygame.init()

# Crear la pantalla
screen = pygame.display.set_mode((1000, 800))

# Reloj (fija la velocidad del juego a los FPS en vez de depender del hardware)
clock = pygame.time.Clock()
FPS = 60

# Fondo
background = pygame.image.load('background.jpg')

# Sonido
mixer.music.load("background.wav")
mixer.music.play(-1)

# Título e ícono
pygame.display.set_caption("Space Invader")
icon = pygame.image.load('ufo.png')
pygame.display.set_icon(icon)

# Jugador
playerImg = pygame.image.load('player.png')
playerX = 370
playerY = 580
playerX_change = 0
PLAYER_SPEED = 6  # píxeles por frame a 60 FPS (ajustado tras agregar clock.tick)

# Estado independiente por tecla (arregla el bug donde soltar una tecla de
# dirección cancelaba el movimiento aunque la tecla opuesta siguiera presionada)
left_pressed = False
right_pressed = False
space_pressed = False

# Enemigo
enemyImg = []
enemyX = []
enemyY = []
enemyX_change = []
enemyY_change = []
num_of_enemies = 6
ENEMY_SPEED = 3  # antes 1: quedaba muy lento tras limitar los FPS a 60

for i in range(num_of_enemies):
    enemyImg.append(pygame.image.load('enemy.png'))
    enemyX.append(random.randint(0, 736))
    enemyY.append(random.randint(0, 150))
    enemyX_change.append(ENEMY_SPEED)
    enemyY_change.append(40)

# Bala

# Ready - La bala no es visible en pantalla
# Fire - La bala está actualmente en movimiento

bulletImg = pygame.image.load('bullet.png')
bulletX = 0
bulletY = 480
bulletX_change = 0
bulletY_change = 18  # antes 10: quedaba muy lenta tras limitar los FPS a 60
bullet_state = "ready"

# Puntaje

score_value = 0
font = pygame.font.Font('freesansbold.ttf', 32)

textX = 10
testY = 10

# Game Over
over_font = pygame.font.Font('freesansbold.ttf', 64)
game_over = False


def show_score(x, y):
    score = font.render("Score : " + str(score_value), True, (255, 255, 255))
    screen.blit(score, (x, y))


def game_over_text():
    over_text = over_font.render("GAME OVER", True, (255, 255, 255))
    screen.blit(over_text, (200, 250))
    restart_text = font.render("Press R to restart", True, (255, 255, 255))
    screen.blit(restart_text, (350, 330))


def reset_game():
    global playerX, bulletY, bullet_state, score_value, game_over
    playerX = 370
    bulletY = 480
    bullet_state = "ready"
    score_value = 0
    game_over = False
    for i in range(num_of_enemies):
        enemyX[i] = random.randint(0, 736)
        enemyY[i] = random.randint(0, 150)
        enemyX_change[i] = ENEMY_SPEED


def player(x, y):
    screen.blit(playerImg, (x, y))


def enemy(x, y, i):
    screen.blit(enemyImg[i], (x, y))


def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    screen.blit(bulletImg, (x + 16, y + 10))


def isCollision(enemyX, enemyY, bulletX, bulletY):
    distance = math.sqrt(math.pow(enemyX - bulletX, 2) + (math.pow(enemyY - bulletY, 2)))
    if distance < 27:
        return True
    else:
        return False


# Bucle del juego
running = True
while running:

    # RGB = Rojo, Verde, Azul
    screen.fill((0, 0, 0))
    # Imagen de fondo
    screen.blit(background, (0, 0))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # si se presiona una tecla, revisar si es izquierda, derecha, espacio o R
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                left_pressed = True
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                right_pressed = True
            if event.key == pygame.K_SPACE:
                space_pressed = True
            if event.key == pygame.K_r and game_over:
                reset_game()

        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                left_pressed = False
            if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                right_pressed = False
            if event.key == pygame.K_SPACE:
                space_pressed = False

    # 5 = 5 + -0.1 -> 5 = 5 - 0.1
    # 5 = 5 + 0.1

    if not game_over:
        # Disparar automáticamente cada frame mientras se mantiene la barra
        # espaciadora presionada, tan pronto la bala anterior vuelve a estar
        # lista (en vez de necesitar una nueva pulsación de tecla)
        if space_pressed and bullet_state == "ready":
            bulletSound = mixer.Sound("laser.wav")
            bulletSound.play()
            bulletX = playerX
            fire_bullet(bulletX, bulletY)

        playerX_change = (int(right_pressed) - int(left_pressed)) * PLAYER_SPEED
        playerX += playerX_change
        if playerX <= 0:
            playerX = 0
        elif playerX >= 736:
            playerX = 736

        # Movimiento de los enemigos
        for i in range(num_of_enemies):

            # Game Over: detener el juego en vez de solo ocultar los enemigos
            if enemyY[i] > 440:
                game_over = True
                break

            enemyX[i] += enemyX_change[i]
            if enemyX[i] <= 0:
                enemyX_change[i] = ENEMY_SPEED
                enemyY[i] += enemyY_change[i]
            elif enemyX[i] >= 736:
                enemyX_change[i] = -ENEMY_SPEED
                enemyY[i] += enemyY_change[i]

            # Colisión
            collision = isCollision(enemyX[i], enemyY[i], bulletX, bulletY)
            if collision:
                explosionSound = mixer.Sound("explosion.wav")
                explosionSound.play()
                bulletY = 480
                bullet_state = "ready"
                score_value += 1
                enemyX[i] = random.randint(0, 736)
                enemyY[i] = random.randint(50, 150)

            enemy(enemyX[i], enemyY[i], i)

        # Movimiento de la bala
        if bulletY <= 0:
            bulletY = 480
            bullet_state = "ready"

        if bullet_state == "fire":
            fire_bullet(bulletX, bulletY)
            bulletY -= bulletY_change
    else:
        game_over_text()

    player(playerX, playerY)
    show_score(textX, testY)
    pygame.display.update()
    clock.tick(FPS)
