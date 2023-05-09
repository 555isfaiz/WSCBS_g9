import threading

class AtomicInt:

    def __init__(self, val=0) -> None:
        self.val = val
        self.lock = threading.Lock()

    def get_and_inc(self) -> int:
        self.lock.acquire()
        ret = self.val
        self.val += 1
        self.lock.release()
        return ret