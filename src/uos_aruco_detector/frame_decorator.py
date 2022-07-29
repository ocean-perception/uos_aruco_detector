import cv2


class Colors:
    # -- BGR colour codes
    RED = (0, 0, 255)
    BLUE = (255, 0, 0)
    GREE = (0, 255, 0)
    YELLOW = (0, 255, 255)
    WHITE = (255, 255, 255)


# -- Function to center the OpenCV text on the frame
def justify(text, frame, font, scale, thickness):
    # Get boundary of this text
    textsize = cv2.getTextSize(text, font, scale, thickness)[0]

    # get coords based on boundary
    textX = (frame.shape[1] - textsize[0]) / 2
    textY = (frame.shape[0] + textsize[1]) / 2
    coord = (int(textX), int(textY))
    return coord


class FrameDecorator:
    def __init__(self):
        # -- Font for the text in the image
        self.font = cv2.FONT_HERSHEY_PLAIN
        self.scale = 3
        self.thickness = 4

    def draw_text(self, frame, msg, color, coord=None):
        if coord is None:
            coord = justify(msg, frame, self.font, self.scale, self.thickness)
        cv2.putText(
            frame,
            msg,
            coord,
            self.font,
            self.scale,
            color,
            self.thickness,
            cv2.LINE_AA,
        )

    def draw_border(self, frame, color, thickness=20):
        cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), color, thickness)

    def show(self, frame):
        cv2.imshow("Frame", frame)
        cv2.waitKey(1)
