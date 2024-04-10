
class Semaphore:
    def __init__(self, initial_value: int = 1):
        self.value = initial_value

    def wait(self, process=None):
        if self.value <= 0:
            process.clock_tick()
            for p in process.shell.processes:
                p.update_stats()
            if process.op_sys.scheduling_method is self.op_sys.rr:
                process.op_sys.rr.track_gantt()
            self.to_ready(True) # Go to waiting queue and do not increase pcb pc
            return
        self.value -= 1 # continue to receive message and continue program

    def signal(self):
        self.value += 1
