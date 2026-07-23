import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.append(str(ROOT_DIR))

# Import model_run from model.py
from model import model_run
from core.parser import TrackParser
from core.roi_mapper import ROIMapper
from core.event_engine import EventEngine
from core.timeline import TimelineGenerator


def run_pipeline(video_path: str):
    print("=" * 60)
    print("STEP 1: Running Model Detection & Tracking")
    print("=" * 60)

    # 1. RUN MODEL FIRST
    tracks_json_path = model_run(video_path)
    
    if not tracks_json_path:
        raise RuntimeError("Model execution failed.")

    print("\n" + "=" * 60)
    print("STEP 2: Running Analytics Pipeline")
    print("=" * 60)

    # 2. PARSE TRACKS
    parser = TrackParser()
    tracks = parser.load()
    print(f"✓ Parsed {len(tracks)} person detections")

    # 3. ROI MAPPING
    roi_mapper = ROIMapper()
    mapped_tracks = roi_mapper.map_tracks(tracks)
    print("✓ ROI Mapping Completed")

    # 4. EVENT ENGINE
    engine = EventEngine()
    events = engine.process(mapped_tracks)
    print(f"✓ Generated timelines for {len(events)} customer(s)")

    # 5. GENERATE & SAVE OUTPUTS
    timeline = TimelineGenerator()
    outputs = timeline.generate(events)
    output_path = timeline.save(outputs)

    print(f"✓ Timeline Saved : {output_path}")
    print("✓ Analytics Saved : data/analytics.json")
    print("✓ Heatmap Saved : data/heatmap.json")
    print("✓ Paths Saved : data/paths.json")

    print("=" * 60)
    print("Pipeline Completed Successfully")
    print("=" * 60)

    return output_path


if __name__ == "__main__":
    # Standard terminal run fallback
    run_pipeline("sample1.mp4")