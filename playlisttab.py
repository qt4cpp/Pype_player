import os

from PyQt5.QtCore import (Qt, QModelIndex, pyqtSignal, pyqtSlot)
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (QApplication, QPushButton, QLabel, QTabWidget, QInputDialog,
                             QMessageBox, QFileDialog, QAction, QMenu)

from playlistview import PlaylistView
from utility import dialog_for_message, createAction


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

        self.context_menu = QMenu(self)
        self.create_context_menu()

        self.load_playlists()

        self.show()

    def create_context_menu(self):
        self.context_menu.addAction(createAction(self, 'Add Playlist', self.add_playlist))
        self.context_menu.addAction(createAction(self, 'Rename', self.rename_playlist))
        self.context_menu.addAction(createAction(self, 'Save', self.save_current))
        self.context_menu.addAction(createAction(self, 'Open', self.load_playlist))
        self.context_menu.addSeparator()
        self.context_menu.addAction(createAction(self, 'Remove', self.remove_playlist))

    def contextMenuEvent(self, event):
        self.context_menu.exec(event.globalPos())

    def url(self, index=0):
        self.playListView.url(index)

    def open(self):
        self.widget(self.currentIndex()).open()

    def open_directory(self):
        self.currentWidget().open_directory()

    def current_playlist(self):
        return self.currentWidget()

    def add_playlist(self):
        while True:
            title, ok = QInputDialog.getText(self, 'New Playlist name', 'New Playlist name')
            if not ok or not title:
                return False
            elif self.is_used(title):
                msg_box = dialog_for_message("'{0}' is already used.".format(title))
                msg_box.exec()
            else:
                self.addTab(self.create_new(), title)
                return True

    def create_new(self):
        new = PlaylistView()
        new.playlist_double_clicked.connect(self.handle_playlist_double_clicked)
        return new

    def rename_playlist(self):
        original = self.tabText(self.currentIndex())
        while True:
            title, ok = QInputDialog.getText(self, 'Rename Playlist', 'New Playlist name', text=original)
            if not ok or not title:
                return False
            elif self.is_used(title):
                msg_box = dialog_for_message("'{0}' is already used.".format(title))
                msg_box.exec()
            else:
                self.setTabText(self.currentIndex(), title)
                return True

    def remove_playlist(self):
        if self.count() == 1:
            msg_box = dialog_for_message("You can't remove the last tab.")
            msg_box.exec()
            return

        current = self.currentIndex()
        title = self.tabText(current)
        msg_box = dialog_for_message('Do you really want to remove \'{0}\' ?'.format(title),
                                     QMessageBox.Cancel | QMessageBox.Ok)
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

    def load_playlist(self):
        """現在のplaylistからload()を呼ぶためのインターフェース"""
        self.current_playlist().load()


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

    def is_valid_name(self, name):
        if len(name) and not self.is_used():
            return True
        return False

    def is_used(self, name):
        for i in range(self.count()):
            if name == self.tabText(i):
                return True
        return False

    def delete_items(self):
        self.currentWidget().delete_items()

    def handle_playlist_double_clicked(self):
        self.double_clicked.emit()

    def next_tab(self):
        i = self.currentIndex()
        if i == self.count()-1:
            self.setCurrentIndex(0)
        else:
            self.setCurrentIndex(i+1)

    def previous_tab(self):
        i = self.currentIndex()
        if i == 0:
            self.setCurrentIndex(self.count()-1)
        else:
            self.setCurrentIndex(i-1)

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)

    playlist = PlaylistTab()
    sys.exit(app.exec_())