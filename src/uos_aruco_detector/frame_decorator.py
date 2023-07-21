import cv2
from .version import __version__


class Colors:
    # -- BGR colour codes
    RED = (0, 0, 255)
    BLUE = (255, 0, 0)
    GREEN = (0, 255, 0)
    YELLOW = (0, 255, 255)
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)


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
    def __init__(self, screen_width, screen_height):
        # -- Font for the text in the image
        self.screen_width = screen_width
        self.screen_height = screen_height
        cv2.namedWindow("Frame", cv2.WINDOW_FREERATIO)
        cv2.setWindowProperty("Frame", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    def draw_text(
        self,
        frame,
        msg,
        color,
        coord=None,
        font=cv2.FONT_HERSHEY_COMPLEX_SMALL,
        scale=1,
        thickness=1,
    ):
        if coord is None:
            coord = justify(msg, frame, font, scale, thickness)
        cv2.putText(
            frame,
            msg,
            coord,
            font,
            scale,
            Colors.BLACK,
            thickness + 1,
            cv2.LINE_AA,
        )
        cv2.putText(
            frame,
            msg,
            coord,
            font,
            scale,
            color,
            thickness,
            cv2.LINE_AA,
        )
        return frame

    def draw_border(self, frame, color, thickness=20):
        cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), color, thickness)
        # show version number on the bottom right corner
        self.draw_text(
            frame,
            "v" + str(__version__),
            Colors.WHITE,
            (frame.shape[1] - 100, frame.shape[0] - 30),
            scale=1,
            thickness=1,
            font=cv2.FONT_HERSHEY_PLAIN,
        )
        # Show message to quit on the bottom left corner
        self.draw_text(
            frame,
            "Press 'q' to quit",
            Colors.WHITE,
            (30, frame.shape[0] - 30),
            scale=1,
            thickness=1,
            font=cv2.FONT_HERSHEY_PLAIN,
        )
        return frame

    def stop(self):
        cv2.destroyAllWindows()

    def show(self, frame):
        """Function to show the frame.

        Parameters
        ----------
        frame : np.ndarray
            The frame to be shown.

        Returns
        -------
        bool
            True if the user requested to stop the program, False otherwise.
        """
        frame_resized = cv2.resize(frame, (self.screen_width, self.screen_height))
        cv2.imshow("Frame", frame_resized)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            return True
        else:
            return False
