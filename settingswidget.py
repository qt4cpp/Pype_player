import os

from PySide2.QtCore import QSettings
from PySide2.QtWidgets import QPushButton, QHBoxLayout, QVBoxLayout, QGroupBox, QGridLayout, \
    QDialog, QCheckBox, QLabel, QFileDialog


class settings_widget(QDialog):
    """設定へのアクセスをするインターフェイスを提供する"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # General settings
        general_group = QGroupBox('General:')
        self.path_guide_label = QLabel(self)
        self.path_guide_label.setText('Playlist folder: ')
        self.path_label = QLabel(self)
        self.browse_button = QPushButton('browse', self)

        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_label, 1)
        path_layout.addWidget(self.browse_button)

        self.window_size_chkbox = QCheckBox('Remember window size when close.')

        general_layout = QVBoxLayout()
        general_layout.addWidget(self.path_guide_label)
        general_layout.addLayout(path_layout)
        general_layout.addWidget(self.window_size_chkbox)
        general_group.setLayout(general_layout)

        # player setting
        player_group = QGroupBox('Player Settings:')
        self.play_time_checkbox = QCheckBox('Display remaining time instead of duration.')
        # TODO: function to display remaining_time

        player_layout = QVBoxLayout()
        player_layout.addWidget(self.play_time_checkbox)
        player_group.setLayout(player_layout)

        # Bottom button
        self.save_button = QPushButton('Save', self)
        self.cancel_button = QPushButton('Cancel', self)
        self.reset_button = QPushButton('Reset', self)

        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.save_button)
        bottom_layout.addWidget(self.cancel_button)
        bottom_layout.addWidget(self.reset_button)

        glayout = QGridLayout()
        glayout.addWidget(general_group, 0, 0, 1, 2)
        glayout.addWidget(player_group, 1, 0, 1, 2)
        glayout.addLayout(bottom_layout, 2, 1)

        self.setLayout(glayout)

        # connection
        self.browse_button.clicked.connect(self.browse)
        self.save_button.clicked.connect(self.apply_and_close)
        self.cancel_button.clicked.connect(self.close)
        self.reset_button.clicked.connect(self.reset)

    def show(self):
        self.read_settings()
        self.resize(500, 300)
        super().show()

    def save_settings(self):
        settings = QSettings()
        settings.setValue('playlist/path', self.path_label.text())
        settings.setValue('window/remember', self.window_size_chkbox.isChecked())
        settings.setValue('player/remaining_time', self.play_time_checkbox.isChecked())

    def read_settings(self):
        settings = QSettings()
        self.path_label.setText(
            settings.value('playlist/path', os.getcwd() + '/playlist/'))
        self.window_size_chkbox.setChecked(settings.value('window/remember', True))
        self.play_time_checkbox.setChecked(settings.value('player/remaining_time', False))

    def apply_and_close(self):
        self.save_settings()
        self.close()

    def reset(self):
        settings = QSettings()
        settings.clear()
        self.read_settings()

    def browse(self):
        open_dir = self.path_label.text()
        path = QFileDialog.getExistingDirectory(
            self, 'Open directory', open_dir,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
            )
        if path:
            self.path_label.setText(path + '/')
