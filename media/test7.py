# https://codeloop.org/how-to-play-mp4-videos-in-python-pyglet/
import pyglet

vidPath = '1.mp4'
window = pyglet.window.Window()
player = pyglet.media.Player()
source = pyglet.media.StreamingSource()
MediaLoad = pyglet.media.load(vidPath)

player.queue(MediaLoad)
player.play()


@window.event
def on_draw():
    if player.source and player.source.video_format:
        player.get_texture().blit(1, 1)


pyglet.app.run()