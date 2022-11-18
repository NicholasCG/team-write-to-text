# Modified from: https://www.geeksforgeeks.org/pyqt5-create-paint-application/

# importing libraries
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QApplication, QHBoxLayout, QVBoxLayout, QPushButton, QWidget, QMenuBar, QAction, QToolBar
from PyQt5.QtGui import QImage, QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt, QPoint, QSize
import sys
import numpy as np

from dataloader_iam import DataLoaderIAM, Batch
from model import Model, DecoderType
from preprocessor import Preprocessor
from typing import Tuple, List

import cv2

# window class
class DrawingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
 
        # setting title
        self.setWindowTitle("Write-to-Text")
        widget = QWidget()

        # setting geometry to main window
        self.setGeometry(100, 100, 800, 200)

        # creating image object
        self.image = QImage(self.size(), QImage.Format_RGB32)
 
        # # making image color to white
        self.image.fill(Qt.white)
 
        # variables
        # drawing flag
        self.drawing = False
        # default brush size
        self.brushSize = 8
        # default color
        self.brushColor = Qt.black
 
        # QPoint object to tract the point
        self.lastPoint = QPoint()

        # menu bar
        toolbar = QToolBar()
        clear_action = QAction("Clear", self)
        clear_action.triggered.connect(self.clear)
        toolbar.addAction(clear_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save)
        toolbar.addAction(save_action)
        toolbar.setMovable(False)

        # menu_bar.addAction(self.save)
        self.addToolBar(toolbar)

        decoder_mapping = {'bestpath': DecoderType.BestPath,
                    'beamsearch': DecoderType.BeamSearch,
                    'wordbeamsearch': DecoderType.WordBeamSearch}

        with open('../model/charList.txt') as f:
            char_list = list(f.read())
        decoder_type = decoder_mapping['beamsearch']
        
        self.model = Model(char_list, decoder_type, must_restore=True)
 
    # method for checking mouse cicks
    def mousePressEvent(self, event):
 
        # if left mouse button is pressed
        if event.button() == Qt.LeftButton:
            # make drawing flag true
            self.drawing = True
            # make last point to the point of cursor
            self.lastPoint = event.pos()
 
    # method for tracking mouse activity
    def mouseMoveEvent(self, event):
         
        # checking if left button is pressed and drawing flag is true
        if (event.buttons() & Qt.LeftButton) & self.drawing:
             
            # creating painter object
            painter = QPainter(self.image)
             
            # set the pen of the painter
            painter.setPen(QPen(self.brushColor, self.brushSize,
                            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
             
            # draw line from the last point of cursor to the current point
            # this will draw only one step
            painter.drawLine(self.lastPoint, event.pos())
             
            # change the last point
            self.lastPoint = event.pos()
            # update
            self.update()
 
    # method for mouse left button release
    def mouseReleaseEvent(self, event):
 
        if event.button() == Qt.LeftButton:
            # make drawing flag false
            self.drawing = False

    # paint event
    def paintEvent(self, event):
        # create a canvas
        canvasPainter = QPainter(self)
         
        # draw rectangle  on the canvas
        canvasPainter.drawImage(self.rect(), self.image, self.image.rect())
 
    # method for saving canvas
    def save(self):

        channels_count = 4
        b = self.image.bits()
        # sip.voidptr must know size to support python buffer interface
        b.setsize(self.height() * self.width() * channels_count)
        img = np.frombuffer(b, np.uint8).reshape((self.height(), self.width(), channels_count))[:, :, 0]

        # cv2.imshow('original', img)
        preprocessor = Preprocessor((128, 32), dynamic_width=True, padding=16)
        img = preprocessor.process_img(img)
        batch = Batch([img], None, 1)

        # cv2.imshow('processed', img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        recognized, probability = self.model.infer_batch(batch, True)
        print(f'Recognized: "{recognized[0]}"')
        print(f'Probability: {probability[0]}')

        self.clear()
 
    # method for clearing every thing on canvas
    def clear(self):
        # make the whole canvas white
        self.image.fill(Qt.white)
        # update
        self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = DrawingWindow()

    window.show()
    sys.exit(app.exec_())