from PyQt5 import QtWidgets, QtGui, QtCore
from PIL import ImageGrab
import sys

class ScreenshotOverlay(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screenshot Region")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setWindowState(QtCore.Qt.WindowFullScreen)

        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()

        self.setCursor(QtGui.QCursor(QtCore.Qt.CrossCursor))

    def paintEvent(self, event):
        qp = QtGui.QPainter(self)
        qp.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), 2))
        qp.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0, 50)))
        qp.drawRect(QtCore.QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        x1 = min(self.begin.x(), self.end.x())
        y1 = min(self.begin.y(), self.end.y())
        x2 = max(self.begin.x(), self.end.x())
        y2 = max(self.begin.y(), self.end.y())

        self.hide()
        QtWidgets.QApplication.processEvents()
        # Take screenshot of the drawn area
        ImageGrab.grab(bbox=(x1, y1, x2, y2)).save("screenshot.png")
        print(f"📸 Screenshot saved: screenshot.png")
        self.close()
