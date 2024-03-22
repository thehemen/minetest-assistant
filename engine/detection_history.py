from collections import deque

class DetectionHistory:
    def __init__(self, class_names, window, conf, delay):
        self.window = window
        self.conf = conf
        self.delay = delay
        self.now_delay = 0
        self.__history = {k: deque(maxlen=self.window) for k in class_names}

    def update(self, detections):
        detected_classes = []

        for class_name, conf, x, y, w, h in detections:
            detected_classes.append(class_name)

        for class_name in self.__history.keys():
            self.__history[class_name].append(detected_classes.count(class_name))

    def get_text(self):
        class_values = {k: sum(v) for k, v in self.__history.items()}
        text = ''

        for class_name, class_value in sorted(class_values.items(), key=lambda x: x[1]):
            if self.conf <= class_value <= self.window + self.conf:
                space_sign = ' ' if len(text) > 0 else ''
                text += f'{space_sign}{class_name}.'
            elif class_value > self.window + self.conf:
                space_sign = ' ' if len(text) > 0 else ''
                text += f'{space_sign}{class_name}s.'

        if len(text) > 0:
            self.now_delay = self.delay
        else:
            if self.now_delay > 0:
                self.now_delay -= 1
                text = 'Empty.'

        return text

    def clear(self):
        for class_name in self.__history.keys():
            self.__history[class_name].clear()

        self.now_delay = 0
