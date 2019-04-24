
import EditDebugger
import sys
from PyQt5.QtWidgets import QApplication

if __name__ == '__main__':
    app = QApplication(sys.argv)
    e = EditDebugger.GraphApp()
    e.show()
    sys.exit(app.exec_())