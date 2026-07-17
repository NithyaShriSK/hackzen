from config import TRACKS_FILE
from core.utils import load_json
from core.roi_mapper import ROIMapper
from core.event_engine import EventEngine
from core.timeline import TimelineGenerator
from core.video_preprocessor import VideoPreprocessor

def main():
    print("=" * 50)
    print(" Human Activity Timeline Generator ")
    print("=" * 50)

    video_path = "input/supermarket.mp4"  # Change filename if needed

    try:
        preprocessor = VideoPreprocessor(video_path)
        metadata = preprocessor.process()

        print("✓ Video preprocessing completed")
        print(metadata)

    except Exception as e:
        print(e)

    # Load Tracks
    tracks = load_json(TRACKS_FILE)

    if not tracks:
        print("No tracks found.")
        return

    # ROI Mapping
    roi_mapper = ROIMapper()
    mapped_tracks = roi_mapper.map_tracks(tracks)

    print(f"✓ ROI Mapping completed ({len(mapped_tracks)} frames)")

    # Event Detection
    event_engine = EventEngine()
    events = event_engine.process(mapped_tracks)

    print(f"✓ Events generated for {len(events)} persons")

    # Timeline Generation
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