import os

from PyQt5.QtCore import (Qt, QModelIndex, pyqtSignal, pyqtSlot)
from PyQt5.QtWidgets import (QApplication, QPushButton, QLabel, QTabWidget, QInputDialog,
                             QMessageBox, QFileDialog)

from playlistview import PlaylistView


class PlaylistTab(QTabWidget):

    double_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.save_playlist_path = 'playlist/'

        self.addTab(self.create_new(), 'temp')
        self.setCurrentIndex(0)
        self.setUsesScrollButtons(True)
        self.setAcceptDrops(True)
        self.setMovable(True)
        self.setElideMode(Qt.ElideNone)

        self.load_playlists()

        self.show()

    def url(self, index=0):
        self.playListView.url(index)

    def open(self):
        self.widget(self.currentIndex()).open()

    def open_directory(self):
        self.currentWidget().open_directory()

    def current_playlist(self):
        return self.currentWidget()

    def add_playlist(self):
        title, ok = QInputDialog.getText(self, 'New Playlist name', 'New Playlist name')
        if ok and len(title) > 0:
            self.addTab(self.create_new(), title)
            return True
        return False

    def create_new(self):
        new = PlaylistView()
        new.playlist_double_clicked.connect(self.handle_playlist_double_clicked)
        return new

    def rename_playlist(self):
        title = self.tabText(self.currentIndex())
        if title == 'temp':
            msg_box = QMessageBox()
            msg_box.setText("{0} can't be renamed.".format(title))
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
            return False
        title, ok = QInputDialog.getText(self, 'Rename Playlist', 'New Playlist name')
        if ok and len(str(title)) > 0:
            self.setTabText(self.currentIndex(), title)
            return True
        else:
            return False

    def remove_playlist(self):
        msg_box = QMessageBox()
        current = self.currentIndex()
        title = self.tabText(current)
        if title == 'temp':
            msg_box.setText("{0} can't be removed.".format(title))
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec()
            return
        msg_box.setText('Do you really want to remove \'{0}\' ?'.format(title))
        msg_box.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)
        msg_box.setDefaultButton(QMessageBox.Cancel)
        ret = msg_box.exec()
        if ret == QMessageBox.Ok:
            self.remove_file(title)
            self.removeTab(current)
        return title

    def remove_file(self, name=''):
        if os.path.exists(self.save_playlist_path + name):
            os.remove(self.save_playlist_path + name)
            return name
        return False

    def save_current(self):
        """現在のPlaylistを保存する
        
        タイトルをファイル名として、パスをファイルの各行に書き出す。
        """
        name = self.tabText(self.currentIndex())
        url, ok = QFileDialog.getSaveFileUrl(self, 'Save File', name+'.m3u', 'playlist(*.m3u')
        if not ok:
            return False
        url = url.toLocalFile()
        self.current_playlist().save(url)

    def save_all(self):
        """すべてのプレイリストを保存する"""
        os.makedirs(self.save_playlist_path, exist_ok=True)
        for i in range(self.count()):
            title = self.tabText(i)
            if not title == 'temp':
                path = self.save_playlist_path + self.tabText(i) + '.m3u'
                self.widget(i).save(path)

    def remove_files(self):
        """すべてのプレイリストファイルを消去する"""
        import shutil
        shutil.rmtree(self.save_playlist_path)

    def load_playlists(self):
        """プレイリストをフォルダから読み込む。

        デフォルトではplaylist/から読み込もうとする。"""
        import os.path

        path = 'playlist/'
        if not os.path.exists(path):
            return False
        files = os.listdir(path)

        for file in files:
            if os.path.isdir(file) or file[-3:] != 'm3u':
                continue
            new_playlist = self.create_new()
            self.addTab(new_playlist, file[:-4])
            new_playlist.load(path+file)

        return True

    def handle_playlist_double_clicked(self):
        self.double_clicked.emit()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    playlist = PlaylistTab()
    sys.exit(app.exec_())