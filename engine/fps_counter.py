class FPSCounter:
    def __init__(self):
        self.__history = []

    def update(self, time_tick):
        self.__history.append(time_tick)

        while self.__history[-1] - self.__history[0] > 1.0:
            del self.__history[0]

    def get_fps(self):
        return len(self.__history)

    def clear(self):
        self.__history.clear()
