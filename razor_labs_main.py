import multiprocessing
from time import sleep

from common.razor_signal import RazorSignal
from detector_lib.razor_detector import RazorDetector
from presentor_lib.razor_presentor import RazorPresentor
from streamer_lib.razor_streamer import RazorStreamer


class Consumer(multiprocessing.Process):

    def __init__(self, task_queue, result_queue):
        super().__init__()
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()
            if next_task is None:
                # Poison pill means shutdown
                print('%s: Exiting' % proc_name)
                self.task_queue.task_done()
                break
            print('%s: %s' % (proc_name, next_task))
            answer = next_task()
            self.task_queue.task_done()
            self.result_queue.put(answer)
        return


def main():
    # Establish communication queues
    frames_queue = multiprocessing.Queue()
    detection_queue = multiprocessing.JoinableQueue()
    video_path = ''
    # Start consumers
    num_consumers = 3
    print('Creating %d consumers' % num_consumers)
    streamer = RazorStreamer(video_path=video_path, frames_queue=frames_queue)
    detector = RazorDetector(frames_queue=frames_queue, detection_queue=detection_queue)
    presentor = RazorPresentor(detection_queue=detection_queue)

    for process in [streamer, detector, presentor]:
        process.start()

    detection_queue.join()
    presentor.present()

    for process in [streamer, detector, presentor]:
        process.set_signal(RazorSignal.STOP)
    # letting processes opportunity to kill themselves
    sleep(5)
    for process in [streamer, detector, presentor]:
        process.terminate()


if __name__ == '__main__':
    main()
