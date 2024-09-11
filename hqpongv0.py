import pygame
import numpy as np

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2)

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PADDLE_WIDTH, PADDLE_HEIGHT = 10, 60
BALL_SIZE = 20
FPS = 60
BALL_SPEED = 5
PADDLE_SPEED = 5
AI_SPEED = 5  # Speed at which AI paddle moves
WINNING_SCORE = 5  # Score needed to win the game

# Functions
def generate_pulse_wave(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = 0.5 * np.sign(np.sin(2 * np.pi * frequency * t))
    wave = (wave * 32767).astype(np.int16)
    wave = np.stack([wave, wave], axis=1)
    return pygame.sndarray.make_sound(wave)

def generate_noise(duration, sample_rate=44100):
    num_samples = int(sample_rate * duration)
    noise = np.random.randint(-32767, 32767, size=(num_samples, 2), dtype=np.int16)
    return pygame.sndarray.make_sound(noise)

def draw_objects(screen, paddle1, paddle2, ball):
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, paddle1)
    pygame.draw.rect(screen, WHITE, paddle2)
    pygame.draw.ellipse(screen, WHITE, ball)
    pygame.draw.aaline(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT))

def draw_scores(screen, score1, score2):
    font = pygame.font.Font(None, 74)
    score_text = font.render(f"{score1}  {score2}", True, WHITE)
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 20))

def draw_game_over(screen, winner):
    font = pygame.font.Font(None, 74)
    text = f"Game Over! {'Player 1 Wins!' if winner == 1 else 'Player 2 Wins!'}"
    game_over_text = font.render(text, True, WHITE)
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - game_over_text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(3000)  # Display the game over screen for 3 seconds

def move_ai_paddle(paddle2, ball):
    # AI moves the paddle to follow the ball's Y position
    if ball.centery < paddle2.centery:
        paddle2.y -= AI_SPEED
    if ball.centery > paddle2.centery:
        paddle2.y += AI_SPEED

    # Ensure AI paddle stays within screen bounds
    if paddle2.top < 0:
        paddle2.top = 0
    if paddle2.bottom > HEIGHT:
        paddle2.bottom = HEIGHT

# Game Initialization
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pong Game")
clock = pygame.time.Clock()

# Paddles and Ball
paddle1 = pygame.Rect(30, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
paddle2 = pygame.Rect(WIDTH - 30 - PADDLE_WIDTH, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
ball = pygame.Rect(WIDTH // 2 - BALL_SIZE // 2, HEIGHT // 2 - BALL_SIZE // 2, BALL_SIZE, BALL_SIZE)

# Ball Movement
ball_dx, ball_dy = BALL_SPEED, BALL_SPEED

# Generate NES-style sounds
beep_sound = generate_pulse_wave(440, 0.1)  # Pulse wave beep sound
hit_sound = generate_noise(0.1)  # Noise sound for paddle hits

# Scoring
score1 = 0
score2 = 0

# Main Game Loop
running = True
game_over = False
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] and paddle1.top > 0:
            paddle1.y -= PADDLE_SPEED
        if keys[pygame.K_s] and paddle1.bottom < HEIGHT:
            paddle1.y += PADDLE_SPEED

        # AI Movement
        move_ai_paddle(paddle2, ball)

        # Ball Movement
        ball.x += ball_dx
        ball.y += ball_dy

        # Ball Collision with Top and Bottom
        if ball.top <= 0 or ball.bottom >= HEIGHT:
            ball_dy = -ball_dy
            beep_sound.play()

        # Ball Collision with Paddles
        if ball.colliderect(paddle1) or ball.colliderect(paddle2):
            ball_dx = -ball_dx
            hit_sound.play()

        # Ball Reset and Scoring
        if ball.left <= 0:
            score2 += 1
            ball.x = WIDTH // 2 - BALL_SIZE // 2
            ball.y = HEIGHT // 2 - BALL_SIZE // 2
            ball_dx = BALL_SPEED
            ball_dy = BALL_SPEED
            beep_sound.play()

        if ball.right >= WIDTH:
            score1 += 1
            ball.x = WIDTH // 2 - BALL_SIZE // 2
            ball.y = HEIGHT // 2 - BALL_SIZE // 2
            ball_dx = -BALL_SPEED
            ball_dy = BALL_SPEED
            beep_sound.play()

        # Check for Game Over
        if score1 >= WINNING_SCORE or score2 >= WINNING_SCORE:
            game_over = True
            winner = 1 if score1 >= WINNING_SCORE else 2
            draw_game_over(screen, winner)

        draw_objects(screen, paddle1, paddle2, ball)
        draw_scores(screen, score1, score2)
        pygame.display.flip()
        clock.tick(FPS)

pygame.quit()
