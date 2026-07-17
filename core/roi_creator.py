import cv2
import json
from pathlib import Path


class ROICreator:

    def __init__(self, image_path, output_file="data/roi.json"):

        self.image = cv2.imread(str(image_path))

        if self.image is None:
            raise FileNotFoundError(image_path)

        self.display = self.image.copy()

        self.output_file = Path(output_file)

        self.current_points = []
        self.current_name = ""

        self.rois = {}

        cv2.namedWindow("ROI Creator")
        cv2.setMouseCallback("ROI Creator", self.mouse_callback)

    def mouse_callback(self, event, x, y, flags, param):

        if event == cv2.EVENT_LBUTTONDOWN:

            self.current_points.append([x, y])

            cv2.circle(self.display, (x, y), 4, (0, 0, 255), -1)

            if len(self.current_points) > 1:
                cv2.line(
                    self.display,
                    tuple(self.current_points[-2]),
                    tuple(self.current_points[-1]),
                    (0, 255, 0),
                    2,
                )

    def redraw(self):

        self.display = self.image.copy()

        # Draw saved ROIs
        for name, pts in self.rois.items():

            pts_np = [tuple(p) for p in pts]

            for i in range(len(pts_np)):
                cv2.line(
                    self.display,
                    pts_np[i],
                    pts_np[(i + 1) % len(pts_np)],
                    (255, 0, 0),
                    2,
                )

            cv2.putText(
                self.display,
                name,
                pts_np[0],
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 0, 0),
                2,
            )

        # Draw current polygon
        for p in self.current_points:
            cv2.circle(self.display, tuple(p), 4, (0, 0, 255), -1)

        for i in range(len(self.current_points) - 1):
            cv2.line(
                self.display,
                tuple(self.current_points[i]),
                tuple(self.current_points[i + 1]),
                (0, 255, 0),
                2,
            )

    def save_roi(self):

        if len(self.current_points) < 3:
            print("Need at least 3 points.")
            return

        name = input("\nEnter ROI Name : ").strip()

        if not name:
            print("Invalid name.")
            return

        self.rois[name] = self.current_points.copy()

        print(f"✓ Saved ROI : {name}")

        self.current_points = []

        self.redraw()

    def undo(self):

        if self.current_points:
            self.current_points.pop()
            self.redraw()

    def run(self):

        print("\n=========== ROI CREATOR ===========")
        print("Left Click : Add Point")
        print("ENTER      : Save ROI")
        print("U          : Undo Point")
        print("R          : Reset Current ROI")
        print("S          : Save roi.json")
        print("Q          : Save & Quit")
        print("===================================\n")

        while True:

            cv2.imshow("ROI Creator", self.display)

            key = cv2.waitKey(1) & 0xFF

            if key == 13:          # ENTER
                self.save_roi()

            elif key == ord("u"):
                self.undo()

            elif key == ord("r"):
                self.current_points = []
                self.redraw()

            elif key == ord("s"):

                self.output_file.parent.mkdir(exist_ok=True)

                with open(self.output_file, "w") as f:
                    json.dump(self.rois, f, indent=4)

                print("roi.json saved.")

            elif key == ord("q"):

                self.output_file.parent.mkdir(exist_ok=True)

                with open(self.output_file, "w") as f:
                    json.dump(self.rois, f, indent=4)

                print("\nSaved", len(self.rois), "ROIs")
                print(self.output_file)

                break

        cv2.destroyAllWindows()