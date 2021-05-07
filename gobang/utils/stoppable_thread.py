import threading
import time


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self, *args, **kwargs):
        super(StoppableThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def run(self) -> None:
        self.result = super().run()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def get_result(self):
        pass


if __name__ == '__main__':

    def a():
        while True:
            time.sleep(0.5)
            if threading.current_thread().stopped():
                break
            print("A")


    thread = StoppableThread(target=a)
    thread.start()
    time.sleep(5)
    print("main")
    time.sleep(1)
    thread.stop()
    thread.join()
