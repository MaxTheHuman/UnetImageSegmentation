# Create by Packetsss
# Personal use is allowed
# Commercial use is prohibited

# from widgets import *

import io
from PIL import ImageOps
from tensorflow import keras

import sys
import cv2
import qimage2ndarray
import pathlib
from copy import deepcopy
from scripts import Images
import numpy as np
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class Start(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(f"{pathlib.Path(__file__).parent.absolute()}/ui/startup.ui", self)
        self.setWindowIcon(QIcon(f"{pathlib.Path(__file__).parent.absolute()}/icon/icon.png"))

        self.button = self.findChild(QPushButton, "browse")
        self.button.clicked.connect(self.on_click)
        self.files, self.main_window = None, None

    def on_click(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Выберите изображение для обработки", "",
                                                "Image Files (*.jpg *.png *.jpeg *.ico);;All Files (*)")
        if files:
            self.files = files
            self.close()
            self.main_window = Main(self.files) 
            self.main_window.show()


class Main(QWidget):
    def __init__(self, files):
        # initialize
        super().__init__()
        uic.loadUi(f"{pathlib.Path(__file__).parent.absolute()}/ui/main.ui", self)
        self.setWindowIcon(QIcon(f"{pathlib.Path(__file__).parent.absolute()}/icon/icon.png"))
        self.move(120, 100)
        self.img_list, self.rb = [], None
        for f in files:
            self.img_list.append(Images(f))
        self.img_id = 0
        self.img_class = self.img_list[self.img_id]
        self.img = QPixmap(qimage2ndarray.array2qimage(cv2.cvtColor(cv2.resize(self.img_class.img, (600, 450)), cv2.COLOR_BGR2RGB)))

        # find widgets and connect them
        self.vbox = self.findChild(QVBoxLayout, "vbox")
        self.vbox1 = self.findChild(QVBoxLayout, "vbox1")
        self.base_frame = self.findChild(QFrame, "base_frame")
        self.process_button = self.findChild(QPushButton, "process_button")
        self.process_button.clicked.connect(self.filter_frame)
        self.save_button = self.findChild(QPushButton, "save_button")
        self.save_button.clicked.connect(self.click_save)

        # display img
        self.gv = self.findChild(QGraphicsView, "gv")
        self.scene = QGraphicsScene()
        self.scene_img = self.scene.addPixmap(self.img)
        self.gv.setScene(self.scene)

        # self.gv2 = self.findChild(QGraphicsView, "gv2")
        # self.scene2 = QGraphicsScene()
        # self.scene_img2 = self.scene2.addPixmap(self.img)
        # self.gv2.setScene(self.scene2)

        # zoom in
        self.zoom_moment = False
        self._zoom = 0

        # misc
        self.rotate_value, self.brightness_value, self.contrast_value, self.saturation_value = 0, 0, 1, 0
        self.flip = [False, False]
        self.zoom_factor = 1

    def update_img(self, movable=False):
        self.img = QPixmap(qimage2ndarray.array2qimage(cv2.cvtColor(self.img_class.img, cv2.COLOR_BGR2RGB)))
        self.scene.removeItem(self.scene_img)
        self.scene_img = self.scene.addPixmap(self.img)
        if movable:
            self.scene_img.setFlag(QGraphicsItem.ItemIsMovable)
        else:
            self.fitInView()

    def get_zoom_factor(self):
        return self.zoom_factor

    def filter_frame(self):
        # nparr = np.frombuffer(request.files['file'].read(), np.uint8)        
        # decode image
        img = self.img_list[0].img
        img_size = (160, 160)
        resized_image = cv2.resize(img, img_size)

        # load pretrained model
        model = keras.models.load_model('/Users/m.siplivy/unet_service/trained_model_copy')
        resized_image = np.reshape(resized_image, [1, 160, 160, 3])
        
        pred = model.predict(resized_image)
        
        mask = np.argmax(pred[0], axis=-1)
        mask = np.expand_dims(mask, axis=-1)
        mask = ImageOps.autocontrast(keras.preprocessing.image.array_to_img(mask))
        # b = io.BytesIO()
        # mask.save(b, 'jpeg')
        # im_bytes = b.getvalue()
        self.img2 = QPixmap(qimage2ndarray.array2qimage(cv2.cvtColor(cv2.resize(np.array(mask), (600, 450)), cv2.COLOR_BGR2RGB)))
        self.gv2 = self.findChild(QGraphicsView, "gv2")
        self.scene2 = QGraphicsScene()
        self.scene_img2 = self.scene2.addPixmap(self.img2)
        self.gv2.setScene(self.scene2)

        # filter_frame = Filter(self)
        # self.base_frame.setParent(None)
        # self.vbox.addWidget(filter_frame.frame)

    def click_save(self):
        try:
            file, _ = QFileDialog.getSaveFileName(self, 'Save File', f"{self.img_class.img_name}."
                                                                     f"{self.img_class.img_format}",
                                                  "Image Files (*.jpg *.png *.jpeg *.ico);;All Files (*)")
            self.img_class.save_img(file)
        except Exception:
            pass

    def wheelEvent(self, event):
        if self.zoom_moment:
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.gv.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def fitInView(self):
        rect = QRectF(self.img.rect())
        if not rect.isNull():
            self.gv.setSceneRect(rect)

            unity = self.gv.transform().mapRect(QRectF(0, 0, 1, 1))
            self.gv.scale(1 / unity.width(), 1 / unity.height())
            view_rect = self.gv.viewport().rect()
            scene_rect = self.gv.transform().mapRect(rect)
            factor = min(view_rect.width() / scene_rect.width(),
                         view_rect.height() / scene_rect.height())
            self.gv.scale(factor, factor)
            self._zoom = 0
            self.zoom_factor = factor


def main():
    app = QApplication(sys.argv)
    window = Start()
    window.show()
    app.exec_()


if __name__ == "__main__":
    main()

