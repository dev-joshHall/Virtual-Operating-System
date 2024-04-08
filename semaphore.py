
class Semaphore:
    def __init__(self, initial_value: int = 1):
        self.value = initial_value

    def wait(self, process=None):
        while self.value <= 0:
            pass  # Busy waiting
        self.value -= 1

    def signal(self):
        self.value += 1
