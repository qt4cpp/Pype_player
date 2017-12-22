from PyQt5.QtCore import QUrl

try:
    from pymediainfo import MediaInfo
except ImportError:
    mediainfo = None


class MediaContent(object):

    def __init__(self, ):
        self.url: QUrl = ''
        self.duration = 0

    def url(self):
        return self.url

    def set_url(self, url: QUrl):
        if not url.isValid():
            return
        if mediainfo is None:
            return
        media_info = MediaInfo.parse(url.toLocalFile())
        for track in media_info.tracks:
            if track.track_type == 'Audio' or track.track_type == 'Video':
                duration = track.duration / 1000
                print(duration)
                print('{0} | {1:.0f}:{2:.0f}'.format(track.Title, duration / 60, duration % 60))
