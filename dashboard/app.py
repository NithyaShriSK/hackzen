import sys
from pathlib import Path

import streamlit as st
import pandas as pd

# Allow imports from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config import TIMELINE_FILE
from core.utils import load_json

st.set_page_config(
    page_title="Human Activity Timeline",
    page_icon="📹",
    layout="wide"
)

st.title("📹 Human Activity Timeline Generator")

timeline = load_json(TIMELINE_FILE)

if not timeline:
    st.warning("No timeline found.\n\nRun:\n\npython main.py")
    st.stop()

persons = sorted(timeline.keys(), key=int)

selected_person = st.sidebar.selectbox(
    "Select Person",
    persons
)

events = timeline[selected_person]

st.subheader(f"Person {selected_person}")

if events:

    df = pd.DataFrame(events)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Timeline")

    for event in events:
        st.markdown(
            f"""
            **{event['time']}**

            ➜ **{event['event']}**

            📍 {event['zone']}

            ---
            """
        )

else:
    st.info("No events found.")

st.sidebar.markdown("---")
st.sidebar.metric("Total Persons", len(persons))
st.sidebar.metric("Events", len(events))