from PyQt5.QtCore import QUrl
from pymediainfo import MediaInfo


class MediaContent():

    def __init__(self, ):
        self.url: QUrl = ''
        self.duration = 0

    def url(self):
        return self.url

    def set_url(self, url: QUrl):
        if not url.isValid():
            return
        media_info = MediaInfo.parse(url.toLocalFile())
        for track in media_info.tracks:
            if track.track_type == 'Audio' or track.track_type == 'Video':
                duration = track.duration / 1000
                print(duration)
                print('{0} | {1:.0f}:{2:.0f}'.format(track.Title, duration / 60, duration % 60))
