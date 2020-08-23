from common.razor_motion import RazorMotionState


class RazorDetectionData:

    def __init__(self, razor_motion_state: RazorMotionState, orig_frame, coordinates):
        self.razor_motion_state = razor_motion_state
        self.orig_frame = orig_frame
        self.coordinates = coordinates
