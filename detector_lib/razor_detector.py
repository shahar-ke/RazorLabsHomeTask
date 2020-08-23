import multiprocessing
from time import sleep

import cv2
import imutils

from common.razor_detection_data import RazorDetectionData
from common.razor_stream_data import FrameStreamData
from common.razor_motion import RazorMotionState
from common.razor_process import RazorProcess
from common.razor_signal import RazorSignal


class RazorDetector(RazorProcess):

    def __init__(self,
                 frames_queue: multiprocessing.Queue,
                 detection_queue: multiprocessing.JoinableQueue,
                 min_area: int = 500):
        super().__init__()
        self.frames_queue = frames_queue
        self.detection_queue = detection_queue
        self.min_area = min_area

    def run(self):
        while True:
            if self.signal == RazorSignal.STOP:
                break
            if self.frames_queue.empty():
                sleep(0.1)
                continue
            while not self.frames_queue.empty():
                frame_detection_data: FrameStreamData = self.frames_queue.get()

                # compute the absolute difference between the current frame and
                # first frame
                frame_delta = cv2.absdiff(frame_detection_data.first_frame, frame_detection_data.processed_frame)
                thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]

                # dilate the thresholded image to fill in holes, then find contours
                # on thresholded image
                thresh = cv2.dilate(thresh, None, iterations=2)
                cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                        cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)
                motion_state = RazorMotionState.NO_MOTION
                coordinates = None
                # loop over the contours
                for c in cnts:
                    # if the contour is too small, ignore it
                    if cv2.contourArea(c) < self.min_area:
                        continue

                    # compute the bounding box for the contour, draw it on the frame,
                    # and update the text
                    (x, y, w, h) = cv2.boundingRect(c)
                    coordinates = (x, y, w, h)
                self.detection_queue.put(RazorDetectionData(razor_motion_state=motion_state,
                                                            orig_frame=frame_detection_data.orig_frame,
                                                            coordinates=coordinates))

            # cleanup the camera and close any open windows
            vs.stop() if args.get("video", None) is None else vs.release()
            cv2.destroyAllWindows()
