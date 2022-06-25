import vlc
# p = subprocess.Popen('cvlc', 'fullscreen', 'home/pi/demo.mp4', '--loop')
doTrashCode = False
player = vlc.MediaPlayer("3.mp4")


def start():
    player.set_fullscreen(True)
    em = player.event_manager()
    em.event_attach(vlc.EventType.MediaPlayerEndReached, onEnd)
    player.play()
    player.set_fullscreen(True)


def onEnd(event):
    global doTrashCode
    if event.type == vlc.EventType.MediaPlayerEndReached:
        doTrashCode = True


def back():
    player.set_media(player.get_media())
    player.play()


start()

while True:
    if doTrashCode:
        back()
        doTrashCode = False
