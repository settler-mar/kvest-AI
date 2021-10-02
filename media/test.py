from pygame import mixer
from time import sleep

mixer.init()
mixer.music.load("test.mp3")
mixer.music.play()

volume = 0
i = 0

while i < 30:
    # mixer.music.play(loops=10, start=0.0)
    sleep(.2)
    volume += 1
    mixer.music.set_volume((volume % 10)/10)
    i = i + 1
    print(volume)

sleep(10)
