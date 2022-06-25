from time import sleep
import vlc

finish = 0
# creating vlc media player object
media_player = vlc.MediaPlayer()
i = vlc.Instance('--no-audio', '--fullscreen')

# https://stackoverflow.com/questions/3595649/vlc-python-eventmanager-callback-type
def SongFinished(event):
    print("\nEvent reports - finished")
    # media_player.set_time(0)
    # media = vlc.Media("5.mp4")
    # media_player.set_media(media)
    # media_player.play()
    # print(0)


media_player.toggle_fullscreen()
events = media_player.event_manager()
events.event_attach(vlc.EventType.MediaPlayerEndReached, SongFinished)

media = vlc.Media("3.mp4")
media_player.set_media(media)
media_player.play()
media_player.toggle_fullscreen()

print('start sleep')
sleep(11)
# media_player.set_time(0)
#
media = vlc.Media("5.mp4")
media_player.set_media(media)
# media_player.set_time(0)
media_player.play()
media_player.toggle_fullscreen()

print('start sleep')
sleep(20000)
