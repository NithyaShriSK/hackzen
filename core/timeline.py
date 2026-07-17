from collections import defaultdict
from core.utils import save_json
from config import TIMELINE_FILE


class TimelineGenerator:
    def __init__(self):
        self.timeline = defaultdict(list)

    def generate(self, events):
        """
        Input:
        {
            1: [
                {
                    "timestamp": "...",
                    "event": "...",
                    "zone": "..."
                }
            ]
        }

        Output:
        {
            "1": [
                {
                    "time": "...",
                    "event": "...",
                    "zone": "..."
                }
            ]
        }
        """

        result = {}

        for person_id, person_events in events.items():

            # Sort by timestamp
            person_events = sorted(
                person_events,
                key=lambda x: x["timestamp"]
            )

            timeline = []
            previous = None

            for event in person_events:

                current = (
                    event["event"],
                    event["zone"]
                )

                # Remove consecutive duplicate events
                if current == previous:
                    continue

                timeline.append({
                    "time": event["timestamp"],
                    "event": event["event"],
                    "zone": event["zone"]
                })

                previous = current

            result[str(person_id)] = timeline

        save_json(result, TIMELINE_FILE)

        return result