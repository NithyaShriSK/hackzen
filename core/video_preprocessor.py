import cv2
import json
from pathlib import Path


class VideoPreprocessor:
    def __init__(self, video_path, output_dir="processed_video"):
        self.video_path = Path(video_path)
        self.output_dir = Path(output_dir)

        self.frames_dir = self.output_dir / "frames"
        self.metadata_dir = self.output_dir / "metadata"

        self.frames_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_dir.mkdir(parents=True, exist_ok=True)

    def process(self):

        cap = cv2.VideoCapture(str(self.video_path))

        if not cap.isOpened():
            raise Exception("Unable to open video.")

        fps = cap.get(cv2.CAP_PROP_FPS)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps

        frame_number = 0

        while True:

            ret, frame = cap.read()

            if not ret:
                break

            frame_name = f"frame_{frame_number:05d}.jpg"

            cv2.imwrite(
                str(self.frames_dir / frame_name),
                frame
            )

            frame_number += 1

        cap.release()

        metadata = {
            "video_name": self.video_path.name,
            "fps": fps,
            "width": width,
            "height": height,
            "frame_count": frame_count,
            "duration_seconds": round(duration, 2)
        }

        with open(
            self.metadata_dir / "video_info.json",
            "w"
        ) as f:
            json.dump(metadata, f, indent=4)

        return metadata