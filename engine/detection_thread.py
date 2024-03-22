from PyQt5 import QtCore
from ultralytics import YOLO
from ultralytics.data.loaders import LoadScreenshots

def to_cpu(x):
    return x.cpu().detach().numpy()

class DetectionThread(QtCore.QThread):
    detectionSignal = QtCore.pyqtSignal(object)

    def __init__(self, parent, model_name, conf, iou):
        QtCore.QThread.__init__(self, parent)
        self.model_name = model_name
        self.conf = conf
        self.iou = iou
        self.active = True

    def addDetectionListener(self, listener):
        self.detectionSignal.connect(listener)

    def run(self):
        model = YOLO(self.model_name, task='detect')
        dataset = LoadScreenshots('screen')

        for path, im, im0s in dataset:
            if not self.active:
                break

            detections = []
            results = model(im, conf=self.conf, iou=self.iou, verbose=False)

            detection = results[0].boxes
            class_names = results[0].names

            if len(detection.cls) > 0:
                classes = to_cpu(detection.cls)
                confidences = to_cpu(detection.conf)
                bboxes = to_cpu(detection.xyxy)

                for class_id, confidence, bbox in zip(classes, confidences, bboxes):
                    class_name = class_names[int(class_id)]
                    conf = float(confidence)
                    x1, y1, x2, y2 = list(bbox.round().astype(int))
                    x, y, w, h = x1, y1, x2 - x1, y2 - y1
                    detections.append(tuple((class_name, conf, x, y, w, h)))

            self.detectionSignal.emit(detections)
