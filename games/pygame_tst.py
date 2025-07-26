import pygame
import sys

# Создание окна
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Тест Pygame")

# Цвета
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Главный цикл
running = True
clock = pygame.time.Clock()

while running:
  screen.fill(WHITE)

  # Рисуем круг в центре
  pygame.draw.circle(screen, RED, (WIDTH // 2, HEIGHT // 2), 50)

  # Обработка событий
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

    elif event.type == pygame.MOUSEBUTTONDOWN:
      print("Нажатие мыши:", event.pos)

  # Обновление экрана
  pygame.display.flip()
  clock.tick(60)  # Ограничение до 60 FPS

pygame.quit()
sys.exit()
