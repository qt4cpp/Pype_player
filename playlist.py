from PySide2.QtCore import Signal, QObject, QSettings
from PySide2.QtWidgets import QApplication

from playlisttab import PlaylistTab
from playlistview import PlaylistView


class Playlist(QObject):

    double_clicked = Signal()

    def __init__(self, parent=None):
        super(Playlist, self).__init__(parent)

        self.widget = PlaylistTab(parent=parent)
        self.widget.double_clicked.connect(self.handle_double_clicked)
        self.using_playlist: PlaylistView = self.widget.widget(0)

        self.widget.show()

    def read_settings(self):
        settings = QSettings()
        settings.beginGroup('playlist')
        self.widget.saved_playlists_path = settings.value('path')
        settings.endGroup()

    def playlist(self):
        return self.widget.current_playlist()

    def change_using_playlist(self):
        self.using_playlist.deactivate()
        self.using_playlist = self.playlist()

    def open(self):
        self.playlist().open()

    def open_directory(self):
        self.playlist().open_directory()

    def get_new_one(self):
        if self.using_playlist is not self.playlist():
            self.change_using_playlist()
        selected_url = self.using_playlist.selected()
        if selected_url:
            self.using_playlist.set_current_index(selected_url)
        elif not self.using_playlist.current_index.isValid():
            self.using_playlist.set_current_index_from_row(0)
        return self.current_url()

    def current_url(self):
        return self.using_playlist.current_url()

    def current_title(self):
        return self.using_playlist.current_title()

    def next(self):
        return self.using_playlist.next()

    def previous(self):
        return self.using_playlist.previous()

    def current_row(self):
        return self.using_playlist.current_row()

    def first(self):
        self.using_playlist.set_current_index_from_row(0)
        return self.current_url()

    def count(self):
        return self.using_playlist.count()

    def update_listview(self):
        self.using_playlist.selectAll()
        self.using_playlist.clearSelection()

    def save_all(self):
        """ファイル開いて、widgetに渡すのがいいのか"""
        self.widget.save_all()

    def disable_current_index(self):
        self.using_playlist.set_current_index_from_row(-1)

    def handle_double_clicked(self):
        self.change_using_playlist()
        self.double_clicked.emit()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    playlist = Playlist()
    sys.exit(app.exec_())
