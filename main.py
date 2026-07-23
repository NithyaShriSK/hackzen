from config import TRACKS_FILE
from core.utils import load_json
from core.roi_mapper import ROIMapper
from core.event_engine import EventEngine
from core.timeline import TimelineGenerator
from core.video_preprocessor import VideoPreprocessor
from model import model_run

def main():
    print("=" * 50)
    print(" Human Activity Timeline Generator ")
    print("=" * 50)

    # Run model to generate tracking data
    print("Running model to generate tracking data...")
    model_run()
    print("✓ Model execution completed")

    # video_path = "sample1.mp4"  # Change filename if needed

    # try:
    #     preprocessor = VideoPreprocessor(video_path)
    #     metadata = preprocessor.process()

    #     print("✓ Video preprocessing completed")
    #     print(metadata)

    # except Exception as e:
    #     print(e)

    # 1. Load Tracks FIRST
    try:
        tracks = load_json(TRACKS_FILE)
    except Exception:
        tracks = load_json("data/tracks.json")

    if not tracks:
        print("No tracks found.")
        return

    # 2. Extract track dicts if tracks.json is structured by frame or track_id
    all_track_objects = []

    if isinstance(tracks, dict):
        for key, val in tracks.items():
            if isinstance(val, list):
                # Frame-based dict e.g., {"0": [{track1}, {track2}]}
                all_track_objects.extend(val)
            elif isinstance(val, dict):
                # ID-based dict e.g., {"track_1": {track1}}
                all_track_objects.append(val)
    elif isinstance(tracks, list):
        all_track_objects = tracks

    # 3. ROI Mapping
    roi_mapper = ROIMapper()
    mapped_tracks = roi_mapper.map_tracks(all_track_objects)

    print(f"✓ ROI Mapping completed ({len(mapped_tracks)} track instances)")

    # 4. Event Detection
    event_engine = EventEngine()
    events = event_engine.process(mapped_tracks)

    print(f"✓ Events generated for {len(events)} persons")

    # 5. Timeline Generation
    timeline_generator = TimelineGenerator()
    timeline = timeline_generator.generate(events)

    print("✓ Timeline saved successfully.")

    print("\n========== SUMMARY ==========")
    for person_id, person_events in timeline.items():
        print(f"\nPerson {person_id}")

        for event in person_events:
            print(
                f"{event['time']}  |  "
                f"{event['event']}  |  "
                f"{event['zone']}"
            )


if __name__ == "__main__":
    main()