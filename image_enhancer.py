import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QSlider, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from PIL import Image, ImageEnhance, ImageFilter
from qimage2ndarray import array2qimage
import numpy as np

class ImageEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Image Editor')
        self.setGeometry(100, 100, 800, 600)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)

        self.brightness_slider = self.create_slider(-100, 100, 0, self.adjust_brightness)
        self.contrast_slider = self.create_slider(-100, 100, 0, self.adjust_contrast)
        self.saturation_slider = self.create_slider(-100, 100, 0, self.adjust_saturation)
        self.exposure_slider = self.create_slider(-100, 100, 0, self.adjust_exposure)
        self.temperature_slider = self.create_slider(-100, 100, 0, self.adjust_temperature)
        self.gamma_slider = self.create_slider(0, 200, 100, self.adjust_gamma)
        self.clarity_slider = self.create_slider(0, 20, 0, self.adjust_clarity)
        self.vignette_slider = self.create_slider(0, 100, 0, self.adjust_vignette)

        load_button = QPushButton('Load Image')
        load_button.clicked.connect(self.load_image)

        save_button = QPushButton('Save Image')
        save_button.clicked.connect(self.save_image)

        slider_layout = QVBoxLayout()
        slider_layout.addWidget(QLabel('Brightness'))
        slider_layout.addWidget(self.brightness_slider)
        slider_layout.addWidget(QLabel('Contrast'))
        slider_layout.addWidget(self.contrast_slider)
        slider_layout.addWidget(QLabel('Saturation'))
        slider_layout.addWidget(self.saturation_slider)
        slider_layout.addWidget(QLabel('Exposure'))
        slider_layout.addWidget(self.exposure_slider)
        slider_layout.addWidget(QLabel('Temperature'))
        slider_layout.addWidget(self.temperature_slider)
        slider_layout.addWidget(QLabel('Gamma'))
        slider_layout.addWidget(self.gamma_slider)
        slider_layout.addWidget(QLabel('Clarity'))
        slider_layout.addWidget(self.clarity_slider)
        slider_layout.addWidget(QLabel('Vignette'))
        slider_layout.addWidget(self.vignette_slider)

        button_layout = QHBoxLayout()
        button_layout.addWidget(load_button)
        button_layout.addWidget(save_button)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.image_label)
        main_layout.addLayout(slider_layout)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        self.original_image = None
        self.modified_image = None

    def create_slider(self, min_value, max_value, default_value, callback):
        slider = QSlider(Qt.Horizontal)
        slider.setMinimum(min_value)
        slider.setMaximum(max_value)
        slider.setValue(default_value)
        slider.valueChanged.connect(callback)
        return slider

    def load_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open Image', '', 'Image Files (*.png *.jpg *.bmp)', options=options)
        if file_name:
            self.original_image = Image.open(file_name).convert('RGB')
            self.modified_image = self.original_image.copy()
            self.update_image_label()

    def save_image(self):
        if self.modified_image:
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(self, 'Save Image', '', 'Image Files (*.png *.jpg *.bmp)', options=options)
            if file_name:
                self.modified_image.save(file_name)


    def update_image_label(self):
        if self.modified_image:
            # Convert PIL image to NumPy array
            np_array = np.array(self.modified_image)
        
            # Convert NumPy array to QImage
            qimage = array2qimage(np_array)
        
            pixmap = QPixmap.fromImage(qimage)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def adjust_brightness(self, value):
        if self.original_image:
            enhancer = ImageEnhance.Brightness(self.original_image)
            self.modified_image = enhancer.enhance(1 + value / 100)
            self.update_image_label()

    def adjust_contrast(self, value):
        if self.original_image:
            enhancer = ImageEnhance.Contrast(self.original_image)
            self.modified_image = enhancer.enhance(1 + value / 100)
            self.update_image_label()

    def adjust_saturation(self, value):
        if self.original_image:
            enhancer = ImageEnhance.Color(self.original_image)
            self.modified_image = enhancer.enhance(1 + value / 100)
            self.update_image_label()

    def adjust_exposure(self, value):
        if self.original_image:
            self.modified_image = self.original_image.copy()
            self.modified_image = self.modified_image.point(lambda p: p * (1 + value / 100))
            self.update_image_label()

    def adjust_temperature(self, value):
        if self.original_image:
            r, g, b = self.original_image.split()
            if value > 0:
                r = r.point(lambda p: p + value)
                b = b.point(lambda p: p - value)
            else:
                r = r.point(lambda p: p - abs(value))
                b = b.point(lambda p: p + abs(value))
            self.modified_image = Image.merge('RGB', (r, g, b))
            self.update_image_label()

    def adjust_gamma(self, value):
        if self.original_image:
            gamma = value / 100
            self.modified_image = self.original_image.copy()
            self.modified_image = self.modified_image.point(lambda p: 255 * ((p / 255) ** gamma))
            self.update_image_label()

    def adjust_clarity(self, value):
        if self.original_image:
            self.modified_image = self.original_image.copy()
            self.modified_image = self.modified_image.filter(ImageFilter.UnsharpMask(radius=2, percent=value * 10, threshold=0))
            self.update_image_label()

    def adjust_vignette(self, value):
        if self.original_image:
            self.modified_image = self.original_image.copy()
            width, height = self.modified_image.size
            center_x = width // 2
            center_y = height // 2
            max_distance = (center_x ** 2 + center_y ** 2) ** 0.5
            for x in range(width):
                for y in range(height):
                    distance = ((x - center_x) ** 2 + (y - center_y) ** 2) ** 0.5
                    factor = 1 - (distance / max_distance) * (value / 100)
                    r, g, b = self.modified_image.getpixel((x, y))
                    self.modified_image.putpixel((x, y), (int(r * factor), int(g * factor), int(b * factor)))
            self.update_image_label()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = ImageEditor()
    editor.show()
    sys.exit(app.exec_())
