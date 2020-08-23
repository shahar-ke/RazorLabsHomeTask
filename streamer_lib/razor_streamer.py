import multiprocessing

import cv2
import imutils

from common.razor_stream_data import FrameStreamData
from common.razor_process import RazorProcess
from common.razor_signal import RazorSignal


class RazorStreamer(RazorProcess):

    def __init__(self, video_path: str, frames_queue: multiprocessing.Queue):
        super().__init__()
        self.video_path = video_path
        self.frames_queue = frames_queue

    def run(self):
        vs = cv2.VideoCapture(self.video_path)
        first_frame = None
        while True:
            if self.signal == RazorSignal.STOP:
                break
            # grab the current frame and initialize the occupied/unoccupied
            # text
            frame = vs.read()
            # if the frame could not be grabbed, then we have reached the end
            # of the video
            if frame is None:
                break
            # resize the frame, convert it to grayscale, and blur it
            frame = imutils.resize(frame, width=500)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)

            # if the first frame is None, initialize it
            if first_frame is None:
                first_frame = gray
                continue
            self.frames_queue.put(FrameStreamData(first_frame=first_frame, orig_frame=frame, processed_frame=gray))
