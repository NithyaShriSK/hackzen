from collections import defaultdict

from config import (
    OUTSIDE,
    ENTRANCE,
    EXIT,
    CHECKOUT,
    SPECIAL_ZONES,
    EVENT_ENTER,
    EVENT_EXIT,
    EVENT_CHECKOUT,
    EVENT_ZONE_VISIT,
    EVENT_ZONE_CHANGE,
)


class EventEngine:
    def __init__(self):
        self.person_state = defaultdict(
            lambda: {
                "current_zone": OUTSIDE,
                "events": [],
            }
        )

    def _add_event(self, person_id, timestamp, event, zone):
        self.person_state[person_id]["events"].append(
            {
                "timestamp": timestamp,
                "event": event,
                "zone": zone,
            }
        )

    def process(self, mapped_tracks):
        """
        Input:
            Tracks with zone information.

        Output:
            {
                person_id: [
                    {
                        "timestamp": "...",
                        "event": "...",
                        "zone": "..."
                    }
                ]
            }
        """

        for track in mapped_tracks:

            pid = track["person_id"]
            timestamp = track["timestamp"]
            zone = track["zone"]

            state = self.person_state[pid]

            previous_zone = state["current_zone"]

            # Ignore duplicate frames in same zone
            if previous_zone == zone:
                continue

            # Enter Store
            if previous_zone == OUTSIDE and zone == ENTRANCE:
                self._add_event(pid, timestamp, EVENT_ENTER, zone)

            # Exit Store
            elif zone == EXIT:
                self._add_event(pid, timestamp, EVENT_EXIT, zone)

            # Checkout
            elif zone == CHECKOUT:
                self._add_event(pid, timestamp, EVENT_ZONE_VISIT, zone)

            # Any business zone except special zones
            elif zone not in SPECIAL_ZONES:
                self._add_event(
                                pid,
                                timestamp,
                                EVENT_ZONE_CHANGE,
                                zone
                            )

            # Generic movement
            elif zone != previous_zone:
                self._add_event(pid, timestamp, f"Moved to {zone}", zone)

            state["current_zone"] = zone

        return {
            pid: data["events"]
            for pid, data in self.person_state.items()
        }