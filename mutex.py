class Mutex:
    def __init__(self):
        self.locked = False

    def acquire(self):
        while self.locked:
            pass  # Busy waiting
        self.locked = True

    def release(self):
        self.locked = False
