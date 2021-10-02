from moviepy.editor import *

import pygame

pygame.init()

pygame.display.set_caption('Show Video on screen')

video = VideoFileClip('2.mp4')
video.resize((600, 100)).preview()
print(10)
pygame.quit()