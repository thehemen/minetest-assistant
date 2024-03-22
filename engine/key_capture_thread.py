from PyQt5 import QtCore
from pynput import keyboard

class KeyCaptureThread(QtCore.QThread):
    keyCaptureSignal = QtCore.pyqtSignal(object)

    def __init__(self, parent, bbox_key, text_key, fps_key, exit_key):
        QtCore.QThread.__init__(self, parent)
        self.bbox_key = bbox_key
        self.text_key = text_key
        self.fps_key = fps_key
        self.exit_key = exit_key

    def addKeyCaptureListener(self, listener):
        self.keyCaptureSignal.connect(listener)

    def on_release(self, key):
        match key:
            case keyboard.KeyCode(char=self.bbox_key):
                self.keyCaptureSignal.emit('bbox')
            case keyboard.KeyCode(char=self.text_key):
                self.keyCaptureSignal.emit('text')
            case keyboard.KeyCode(char=self.fps_key):
                self.keyCaptureSignal.emit('fps')
            case keyboard.KeyCode(char=self.exit_key):
                self.keyCaptureSignal.emit('exit')
                return False
            case _:
                pass

    def run(self):
        with keyboard.Listener(on_release=self.on_release) as listener:
            listener.join()
