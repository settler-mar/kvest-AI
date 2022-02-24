# Импортируем модуль для игр pygame
import pygame
import random
import math
from datetime import datetime
from stl import mesh
import numpy

points = []

# your_mesh = mesh.Mesh.from_file('cub.stl')
# your_mesh = mesh.Mesh.from_file('face1.stl')
# points = numpy.resize(your_mesh.points.flatten(), (int(your_mesh.points.size / 3), 3)).tolist()

# Инициализируем движок pygame
pygame.init()

HEIGHT = 800
WIDTH = 800

AMOUNTX = 40
AMOUNTY = 20
SEPARATION = 15
POINT_CNT = AMOUNTX * AMOUNTY
BLACK = [0, 0, 0]
WHITE = [255, 255, 255]

# размеры окна с анимацией
SIZE = [WIDTH, HEIGHT]

screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Snow Animation")

# пустой список
# points = [[0, 0, 0], [0, 10, 0, ], [0, 20, 0, ], [0, 30, 0, ]]

clock = pygame.time.Clock()


def make_poly():
    count = 5
    for ix in range(AMOUNTX + 1):
        for iy in range(AMOUNTY + 1):
            x = ix * SEPARATION - ((AMOUNTX * SEPARATION) / 2) + WIDTH / 2
            y = iy * SEPARATION - ((AMOUNTY * SEPARATION) / 2)
            z = 0
            points.append([x, y, z])


make_poly()
da = 0
points = [x for n, x in enumerate(points) if x not in points[:n]]
print("Points are", len(points), points)


def draw_pixel(point):
    k = 1
    [x, y, z] = [p * k if p else 0.000001 for p in point]
    x = x - WIDTH / 2

    r = (x ** 2 + y ** 2) ** 0.5
    if x > 0 and y >= 0:
        a = math.atan(y / x)
    elif x > 0 and y < 0:
        a = math.atan(y / x) + 2 * 3.14
    elif x < 0:
        a = math.atan(y / x) + 3.14
    elif x == 0 and y > 0:
        a = 3.14 / 2
    else:
        a = 3 * 3.14 / 2
    a = a + da / (3.14 * 90)
    x = r * math.cos(a) + WIDTH / 2
    y = r * math.sin(a)
    # print(r, a)

    c = y * 5
    c = c if c > 0 else 0
    c = c if c < 255 else 255
    color = [c, c, c]
    # color = [255, 255, 255]
    dx = y * (x - WIDTH / 2) / 300  # делитель определяет глубину
    pygame.draw.circle(screen, color, [dx + x, y + z + HEIGHT / 2], 2)
    # return [point[0], point[1]]


# Снег будет идти до тех пор пока не нажмется кнопка стоп
done = False
count = 0
dx = 1
while not done:
    for event in pygame.event.get():  # Пользователь сделал что-то
        if event.type == pygame.QUIT:  # Если нажато стоп
            done = True  # выходим из цикла

    # цвет backgrounda
    screen.fill(BLACK)
    i = 0
    for ix in range(AMOUNTX + 1):
        for iy in range(AMOUNTY + 1):
            z = (math.sin((ix + count) * 0.3) * 50) + (math.sin((iy + count) * 0.5) * 50) + 150
            points[i][2] = z
            i += 1

    # обработка каждой снежинки
    for i in range(len(points)):
        draw_pixel(points[i])

        # снежинка вниз на 1
        # snow_list[i][2] += 1

        # if snow_list[i][2] > HEIGHT:
        #     y = random.randrange(-50, -10)
        #     snow_list[i][2] = y
        #     x = random.randrange(0, WIDTH)
        #     snow_list[i][0] = x

    # обновление screen с новыми данными и позициями снежинок
    pygame.display.flip()
    clock.tick(20)
    count += .1
    da += dx
    if da == 60:
        dx = -1
    if da == -60:
        dx = 1

pygame.quit()
