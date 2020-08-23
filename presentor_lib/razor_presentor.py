import datetime
import multiprocessing
from time import sleep

import cv2

from common.razor_detection_data import RazorDetectionData
from common.razor_motion import RazorMotionState
from common.razor_process import RazorProcess
from common.razor_signal import RazorSignal


class RazorPresentor(RazorProcess):

    def __init__(self, detection_queue: multiprocessing.JoinableQueue):
        super().__init__()
        self.detection_queue = detection_queue
        self.processed_frames = list()

    def run(self):
        while True:
            if self.signal == RazorSignal.STOP:
                break
            if self.detection_queue.empty():
                sleep(0.1)
            while not self.detection_queue.empty():
                razor_detection_data: RazorDetectionData = self.detection_queue.get()
                motion_state = razor_detection_data.razor_motion_state
                if motion_state == RazorMotionState.MOTION_DETECTED:
                    coordinated = razor_detection_data.coordinates
                    (x, y, w, h) = coordinated
                    cv2.rectangle(razor_detection_data.orig_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # draw the text and timestamp on the frame
                cv2.putText(razor_detection_data.orig_frame, "Room Status: {}".format(RazorMotionState.value), (10, 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.putText(razor_detection_data.orig_frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),
                            (10, razor_detection_data.orig_frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.35,
                            (0, 0, 255), 1)
                self.processed_frames.append(razor_detection_data.orig_frame)



    def present(self):
        # show the frame and record if the user presses a key
        for frame in self.processed_frames:
            cv2.imshow("Security Feed", frame)
            key = cv2.waitKey(1) & 0xFF

            # if the `q` key is pressed, break from the lop
            if key == ord("q"):
                break
