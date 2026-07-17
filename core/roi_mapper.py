from config import ROI_FILE, OUTSIDE
from core.utils import load_json, bbox_center, point_in_polygon


class ROIMapper:
    def __init__(self):
        self.reload()

    def reload(self):
        self.rois = load_json(ROI_FILE)

    def get_zone(self, bbox):
        if len(bbox) != 4:
            raise ValueError("Bounding box must contain [x1, y1, x2, y2].")

        center = bbox_center(bbox)

        for zone_name, polygon in self.rois.items():
            if point_in_polygon(center, polygon):
                return zone_name

        return OUTSIDE

    def map_tracks(self, tracks):
        mapped_tracks = []

        for track in tracks:
            mapped_track = track.copy()
            mapped_track["zone"] = self.get_zone(track["bbox"])
            mapped_tracks.append(mapped_track)

        return mapped_tracks