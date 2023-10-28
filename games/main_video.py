import pygame
from moviepy.editor import VideoFileClip

# Initialize Pygame
pygame.init()

# Load the video clip
clip = VideoFileClip("video/test.mp4")  # (or .webm, .avi, etc.)
clip.loop(True)
print('size',clip.size)

def getSurface(t, srf=None):
    frame = clip.get_frame(t=t % clip.duration)  # t is the time in seconds

    if srf is None:
        # Transpose the array and create the Pygame surface
        return pygame.surfarray.make_surface(frame.swapaxes(0, 1))
    else:
        pygame.surfarray.blit_array(srf, frame.swapaxes(0, 1))
        return srf


surface = getSurface(0)

screen = pygame.display.set_mode(surface.get_size(), 0, 15)

# Run the Pygame loop to keep the window open
running = True
t = 0
while running:
    # Draw the surface onto the window
    screen.blit(getSurface(t, surface), (0, 0))
    pygame.display.flip()
    t += 1 / 30  # use actual fps here

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.time.delay(20)