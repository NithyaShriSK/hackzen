import sys
import os
import json
import tempfile
from pathlib import Path
import streamlit as st
import pandas as pd

# -------------------------------------------------------------------
# Path Setup: Add project root to sys.path
# -------------------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config import TIMELINE_FILE
from core.utils import load_json
from main import run_pipeline

# -------------------------------------------------------------------
# Page Config & Custom Styling
# -------------------------------------------------------------------
st.set_page_config(
    page_title="RetailPulse AI - Customer Activity Intelligence",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* Hero Header */
    .hero-container {
        text-align: center;
        padding: 2rem 1rem 1.5rem 1rem;
        background: linear-gradient(180deg, #1E293B 0%, #0F172A 100%);
        border-bottom: 1px solid #334155;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    .app-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(90deg, #38BDF8, #818CF8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .app-subtitle {
        font-size: 1.1rem;
        color: #94A3B8;
        font-weight: 400;
    }

    /* Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: 700;
        color: #38BDF8 !important;
    }
    
    /* Custom Timeline Card */
    .timeline-card {
        background-color: #1E293B;
        border-left: 4px solid #38BDF8;
        padding: 14px 18px;
        border-radius: 8px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .timeline-time {
        font-size: 0.9rem;
        color: #38BDF8;
        font-weight: 700;
    }
    .timeline-event {
        font-size: 1.1rem;
        color: #FFFFFF;
        font-weight: 600;
        margin: 4px 0;
    }
    .timeline-zone {
        font-size: 0.85rem;
        color: #94A3B8;
    }

    /* Summary Card Styling */
    .summary-card {
        background-color: #1E293B;
        border: 1px solid #38BDF8;
        border-radius: 8px;
        padding: 18px;
        margin-top: 20px;
    }
    .summary-title {
        color: #38BDF8;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 10px;
    }

    /* Hide Streamlit Default Top Padding */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Session State Initialization to prevent past data from rendering on load
if "processed" not in st.session_state:
    st.session_state.processed = False

# -------------------------------------------------------------------
# Hero Banner
# -------------------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div class="app-title">🛍️ RetailPulse AI</div>
    <div class="app-subtitle">Automated Customer Activity, Dwell-Time & Zone Engagement Analytics</div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# Centered Video Upload & Pipeline Runner
# -------------------------------------------------------------------
up_col1, up_col2, up_col3 = st.columns([1, 2, 1])

with up_col2:
    st.subheader("📹 Upload Retail Surveillance Video")
    uploaded_file = st.file_uploader(
        "Choose video file", 
        type=["mp4", "avi", "mov", "mkv"],
        label_visibility="collapsed"
    )

    if uploaded_file is not None:
        st.success(f"📁 Selected File: **{uploaded_file.name}**")
        
        if st.button("🚀 Process Video Pipeline", use_container_width=True, type="primary"):
            with st.status("Executing Analytics Pipeline...", expanded=True) as status:
                st.write("📥 Saving video payload...")
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    temp_video_path = tmp_file.name

                try:
                    st.write("🧠 Running YOLOv11 Detection & BotSORT Tracking...")
                    st.write("📊 Mapping ROIs and generating timelines...")
                    
                    run_pipeline(temp_video_path)
                    
                    st.session_state.processed = True
                    status.update(label="Processing Complete!", state="complete", expanded=False)
                    st.rerun()
                except Exception as e:
                    st.session_state.processed = False
                    status.update(label="Error Executing Pipeline", state="error", expanded=True)
                    st.error(f"Details: {e}")

# Stop execution if a video hasn't been processed yet in the current session
if not st.session_state.processed:
    st.info("⬆️ Please upload a surveillance video above and click **Process Video Pipeline** to begin analysis.")
    st.stop()

st.markdown("---")

# -------------------------------------------------------------------
# Data Loading & Parsing
# -------------------------------------------------------------------
timeline = load_json(TIMELINE_FILE)

if not timeline:
    st.warning("No tracking analytics were generated. Please re-process the video.")
    st.stop()

events = []
selected_person = None
persons = []

if isinstance(timeline, dict):
    persons = sorted(list(timeline.keys()), key=lambda x: int(x) if str(x).isdigit() else str(x))
    selected_person = st.selectbox("🎯 Select Tracked Customer ID", persons)
    events = timeline[selected_person]

elif isinstance(timeline, list):
    if len(timeline) > 0 and isinstance(timeline[0], dict) and "events" in timeline[0]:
        person_map = {str(item.get("person_id", i)): item.get("events", []) for i, item in enumerate(timeline)}
        persons = sorted(list(person_map.keys()), key=lambda x: int(x) if str(x).isdigit() else str(x))
        selected_person = st.selectbox("🎯 Select Tracked Customer ID", persons)
        events = person_map[selected_person]
    else:
        df_all = pd.DataFrame(timeline)
        id_col = next((col for col in ["person_id", "track_id", "id", "customer_id"] if col in df_all.columns), None)
        if id_col:
            persons = sorted(df_all[id_col].unique().astype(str), key=lambda x: int(x) if x.isdigit() else x)
            selected_person = st.selectbox("🎯 Select Tracked Customer ID", persons)
            events = df_all[df_all[id_col].astype(str) == str(selected_person)].to_dict(orient="records")
        else:
            persons = ["Customer #1"]
            selected_person = "Customer #1"
            events = timeline

# -------------------------------------------------------------------
# Separate Summary Row from Activity Events
# -------------------------------------------------------------------
clean_events = []
summary_data = None

for e in events:
    act = str(e.get('activity', e.get('event', ''))).lower()
    if act == 'summary' or e.get('start') == 'None' or e.get('zone') == 'None':
        summary_data = e.get('summary', None)
    else:
        clean_events.append(e)

# -------------------------------------------------------------------
# Key Performance Metrics Row
# -------------------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("Total Customers Tracked", len(persons))

with m2:
    st.metric("Total Activities Recorded", len(clean_events))

with m3:
    zones = set([e.get('zone', e.get('ROI Location', 'N/A')) for e in clean_events])
    st.metric("Unique Zones Visited", len(zones))

with m4:
    st.metric("Detection Engine", "YOLOv11m + BotSORT")

st.markdown("<br>", unsafe_allow_html=True)

# -------------------------------------------------------------------
# Full-Width Activity Stream Section
# -------------------------------------------------------------------
st.subheader(f"👤 Activity Stream: Customer #{selected_person}")

tab1, tab2 = st.tabs([" Visual Timeline", "📊 Structured Data Table"])

with tab1:
    if clean_events:
        t_col1, t_col2 = st.columns(2)
        
        for idx, event in enumerate(clean_events):
            start_t = event.get('start', event.get('time', 'N/A'))
            end_t = event.get('end', '')
            time_display = f"{start_t} - {end_t}" if end_t else start_t
            
            activity = event.get('activity', event.get('event', 'N/A'))
            zone = event.get('zone', event.get('ROI Location', 'N/A'))
            duration = event.get('duration', None)
            duration_str = f" • Dwell: {duration}s" if duration else ""

            card_html = f"""
            <div class="timeline-card">
                <div class="timeline-time">⏱️ {time_display}{duration_str}</div>
                <div class="timeline-event">➜ {activity}</div>
                <div class="timeline-zone">📍 Zone: <b>{zone}</b></div>
            </div>
            """
            
            if idx % 2 == 0:
                with t_col1:
                    st.markdown(card_html, unsafe_allow_html=True)
            else:
                with t_col2:
                    st.markdown(card_html, unsafe_allow_html=True)
    else:
        st.info("No timeline activities recorded for this customer.")

with tab2:
    if clean_events:
        df_events = pd.DataFrame(clean_events)
        
        # Remove raw summary column from table view
        if "summary" in df_events.columns:
            df_events = df_events.drop(columns=["summary"])

        st.dataframe(
            df_events, 
            use_container_width=True, 
            hide_index=True
        )
    else:
        st.info("No tabular data available.")

# -------------------------------------------------------------------
# Separate Summary Callout Box (Bottom)
# -------------------------------------------------------------------
if summary_data:
    st.markdown('<div class="summary-card">', unsafe_allow_html=True)
    st.markdown('<div class="summary-title">📝 Customer Journey Summary</div>', unsafe_allow_html=True)
    
    if isinstance(summary_data, str) and summary_data.startswith('{'):
        try:
            parsed_summary = json.loads(summary_data)
            for k, v in parsed_summary.items():
                st.write(f"• **{k.replace('_', ' ').title()}**: {v}")
        except Exception:
            st.write(summary_data)
    else:
        st.write(str(summary_data))
        
    st.markdown('</div>', unsafe_allow_html=True)