import sys
from PyQt5.QtWidgets import QApplication

from pype_player import PypePlayer


if __name__ == '__main__':
    app = QApplication(sys.argv)

    pypePlayer = PypePlayer()
    sys.exit(app.exec_())
