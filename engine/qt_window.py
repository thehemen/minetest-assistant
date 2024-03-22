from time import time
from PyQt5 import QtCore, QtWidgets, QtGui
from engine.detection_thread import DetectionThread
from engine.key_capture_thread import KeyCaptureThread
from engine.detection_history import DetectionHistory
from engine.fps_counter import FPSCounter

class UIConfig:
    def __init__(self, config):
        self.color = {k: v for k, v in zip('rgb', config['color'])}
        self.font_name = config['font_name']
        self.font_size = config['font_size']
        self.alignment = None

        match config['alignment']:
            case 'left':
                self.alignment = QtCore.Qt.AlignLeft
            case 'center':
                self.alignment = QtCore.Qt.AlignCenter
            case 'right':
                self.alignment = QtCore.Qt.AlignRight
            case _:
                pass

        self.used = config['used']

    def get_ui_data(self):
        return self.color, self.font_name, self.font_size, self.alignment

class QtWindow(QtWidgets.QWidget):
    def __init__(self, DR, settings):
        super().__init__()
        screen = DR.primaryScreen()
        size = screen.size()
        w = size.width()
        h = size.height()

        self.resize(w, h)
        self.setWindowTitle('Minetest Assistant')
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint |
                            QtCore.Qt.FramelessWindowHint |
                            QtCore.Qt.X11BypassWindowManagerHint)

        class_names = list(settings['names'].values())
        window, conf, delay = list(map(settings['history'].get, ['window', 'conf', 'delay']))

        self.__history = DetectionHistory(class_names, window, conf, delay)
        self.__detections = []

        self.__fps = FPSCounter()

        model_name, conf, iou = list(map(settings['network'].get, ['filename', 'conf', 'iou']))
        width, height = list(map(settings['resolution'].get, ['width', 'height']))

        self.__detection_thread = DetectionThread(self, model_name, conf, iou)
        self.__detection_thread.addDetectionListener(self.updateOverlay)
        self.__detection_thread.start()

        bbox_key, text_key = list(map(settings['key_capture'].get, ['bbox', 'text']))
        fps_key, exit_key = list(map(settings['key_capture'].get, ['fps', 'exit']))

        self.__key_capture_thread = KeyCaptureThread(self, bbox_key, text_key, fps_key, exit_key)
        self.__key_capture_thread.addKeyCaptureListener(self.modifyOverlay)
        self.__key_capture_thread.start()

        self.bbox = UIConfig(settings['overlay']['bbox'])
        self.text = UIConfig(settings['overlay']['text'])
        self.fps = UIConfig(settings['overlay']['fps'])

        self.text_rect = {'x': int(round(width / 4.0)), 'y': int(round(height * 3.0 / 4.0)),
                          'w': int(round(width / 2.0)), 'h': int(round(height / 8.0))}

        self.fps_rect = {'x': int(round(width / 32.0)), 'y': int(round(height - height / 16.0)),
                         'w': int(round(width / 16.0)), 'h': int(round(height / 8.0))}

    def updateOverlay(self, detections):
        if self.bbox.used:
            self.__detections = detections

        if self.text.used:
            self.__history.update(detections)

        if self.fps.used:
            self.__fps.update(time())

        self.update()

    def modifyOverlay(self, code):
        match code:
            case 'bbox':
                if self.bbox.used:
                    self.__detections.clear()
                    self.bbox.used = False
                else:
                    self.bbox.used = True
            case 'text':
                if self.text.used:
                    self.__history.clear()
                    self.text.used = False
                else:
                    self.text.used = True
            case 'fps':
                if self.fps.used:
                    self.__fps.clear()
                    self.fps.used = False
                else:
                    self.fps.used = True
            case 'exit':
                self.closeOverlay()
            case _:
                pass

    def closeOverlay(self):
        self.__detection_thread.active = False
        self.__detection_thread.quit()
        self.__detection_thread.wait()
        self.__key_capture_thread.quit()
        self.__key_capture_thread.wait()
        self.close()

    def paintEvent(self, e):
        qp = QtGui.QPainter(self)

        if self.bbox.used:
            color, font_name, font_size, alignment = self.bbox.get_ui_data()
            qp.setPen(QtGui.QPen(QtGui.QColor(color['r'], color['g'], color['b'])))
            qp.setFont(QtGui.QFont(font_name, font_size))

            for class_name, conf, x, y, w, h in self.__detections:
                qp.drawRect(x, y, w, h)
                qp.drawText(x + 5, y + 5, w, h, alignment, f'{class_name} {conf:.2f}')

        if self.text.used:
            text = self.__history.get_text()
            rect = self.text_rect
            color, font_name, font_size, alignment = self.text.get_ui_data()
            qp = self.drawText(qp, text, rect, color, font_name, font_size, alignment)

        if self.fps.used:
            text = f'{self.__fps.get_fps()}'
            rect = self.fps_rect
            color, font_name, font_size, alignment = self.fps.get_ui_data()
            qp = self.drawText(qp, text, rect, color, font_name, font_size, alignment)

        qp.end()

    def drawText(self, qp, text, rect, color, font_name, font_size, alignment):
        qp.setPen(QtGui.QPen(QtGui.QColor(color['r'], color['g'], color['b'])))
        qp.setFont(QtGui.QFont(font_name, font_size))
        qp.drawText(rect['x'], rect['y'], rect['w'], rect['h'], alignment, text)
        return qp
