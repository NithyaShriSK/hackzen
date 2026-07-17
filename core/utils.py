import json
from pathlib import Path
from shapely.geometry import Point, Polygon


def load_json(file_path):
    """Load JSON file."""
    path = Path(file_path)

    if not path.exists():
        return {}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data, file_path):
    """Save JSON file."""
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def bbox_center(bbox):
    """
    bbox = [x1, y1, x2, y2]
    Returns center point.
    """
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2, (y1 + y2) / 2)


def point_in_polygon(point, polygon_points):
    """
    Check if point lies inside polygon.
    """
    polygon = Polygon(polygon_points)
    return polygon.contains(Point(point))


def euclidean_distance(p1, p2):
    """
    Calculate Euclidean distance.
    """
    return ((p1[0] - p2[0]) ** 2 +
            (p1[1] - p2[1]) ** 2) ** 0.5


def format_time(seconds):
    """
    Convert seconds to HH:MM:SS
    """
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)

    return f"{h:02}:{m:02}:{s:02}"