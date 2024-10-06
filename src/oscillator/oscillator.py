import time

class HighPrecisionOscillator:
    def __init__(self):
        self.start_time = time.time()
        self.offset = 0

    def get_time(self) -> float:
        return time.time() - self.start_time + self.offset

    def set_offset(self, offset: float):
        self.offset = offset
