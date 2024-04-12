from mutex import Mutex

class Semaphore:
    def __init__(self, initial_value: int = 1):
        self.value = initial_value
        self.mutex_lock = Mutex()

    def wait(self, process=None):
        while self.value <= 0:
            pass # Busy waiting
        self.mutex_lock.acquire()
        self.value -= 1 # continue to receive message and continue program
        self.mutex_lock.release()

    def signal(self):
        self.mutex_lock.acquire()
        self.value += 1
        self.mutex_lock.release()
