import multiprocessing
from abc import abstractmethod, ABC

from common.razor_signal import RazorSignal


class RazorProcess(multiprocessing.Process, ABC):

    def __init__(self):
        super().__init__()
        self.signal: RazorSignal = RazorSignal.RUN

    def set_signal(self, razor_signal: RazorSignal):
        self.signal = razor_signal

    @abstractmethod
    def run(self):
        raise NotImplemented()
