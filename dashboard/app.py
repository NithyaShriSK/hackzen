import sys
from pathlib import Path
import tempfile
import tempfile

import streamlit as st
import pandas as pd

# Allow imports from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from config import TIMELINE_FILE, TRACKS_FILE
from core.utils import load_json
from model import model_run
from core.roi_mapper import ROIMapper
from core.event_engine import EventEngine
from core.timeline import TimelineGenerator
from model import model_run
from core.roi_mapper import ROIMapper
from core.event_engine import EventEngine
from core.timeline import TimelineGenerator

st.set_page_config(
    page_title="Human Activity Timeline",
    page_icon="📹",
    layout="wide"
)

st.title("📹 Human Activity Timeline Generator")

# Center the video upload section
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("### Upload Video")
    uploaded_video = st.file_uploader("Choose a video file", type=["mp4", "avi", "mov"], label_visibility="collapsed")
    
    if uploaded_video:
        st.success(f"Video uploaded: {uploaded_video.name}")
        
        if st.button("Process Video", use_container_width=True, type="primary"):
            # Save uploaded video to temp file (not saved permanently)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                tmp_file.write(uploaded_video.read())
                video_path = tmp_file.name
            
            with st.spinner("Processing video... This may take a while."):
                try:
                    # Step 1: Run model to generate tracking data
                    st.write("🔄 Running YOLO model for object detection and tracking...")
                    model_run(video_path)
                    st.success("✓ Model processing completed")
                    
                    # Step 2: Load tracks
                    st.write("🔄 Loading tracking data...")
                    tracks = load_json(TRACKS_FILE)
                    
                    if not tracks:
                        st.error("No tracks found after model processing.")
                        st.stop()
                    
                    # Step 3: ROI Mapping
                    st.write("🔄 Mapping tracks to ROIs...")
                    roi_mapper = ROIMapper()
                    mapped_tracks = roi_mapper.map_tracks(tracks)
                    st.success(f"✓ ROI Mapping completed ({len(mapped_tracks)} frames)")
                    
                    # Step 4: Event Detection
                    st.write("🔄 Generating events...")
                    event_engine = EventEngine()
                    events = event_engine.process(mapped_tracks)
                    st.success(f"✓ Events generated for {len(events)} persons")
                    
                    # Step 5: Timeline Generation
                    st.write("🔄 Generating timeline...")
                    timeline_generator = TimelineGenerator()
                    timeline = timeline_generator.generate(events)
                    st.success("✓ Timeline saved successfully")
                    
                    st.info("✅ Processing complete! View the timeline below.")
                    
                except Exception as e:
                    st.error(f"Error during processing: {str(e)}")
                    st.stop()
                
                finally:
                    # Clean up temp file (don't save uploaded video permanently)
                    if Path(video_path).exists():
                        Path(video_path).unlink()

# Load existing timeline if available (either from processing or previous runs)
# Initialize session state for tracking processing status
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False

# Center the video upload section
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("### Upload Video")
    uploaded_video = st.file_uploader("Choose a video file", type=["mp4", "avi", "mov"], label_visibility="collapsed")
    
    if uploaded_video:
        st.success(f"Video uploaded: {uploaded_video.name}")
        
        if st.button("Process Video", use_container_width=True, type="primary"):
            # Save uploaded video to temp file (not saved permanently)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                tmp_file.write(uploaded_video.read())
                video_path = tmp_file.name
            
            # Validate the video file before processing
            try:
                import cv2
                test_cap = cv2.VideoCapture(video_path)
                if not test_cap.isOpened():
                    st.error("Invalid video file. Could not open the uploaded video.")
                    Path(video_path).unlink()
                    st.stop()
                test_cap.release()
                st.success("Video file validated successfully")
            except Exception as e:
                st.error(f"Video validation failed: {str(e)}")
                if Path(video_path).exists():
                    Path(video_path).unlink()
                st.stop()
            
            with st.spinner("Processing video... This may take a while."):
                try:
                    # Step 1: Run model to generate tracking data
                    st.write("🔄 Running YOLO model for object detection and tracking...")
                    model_run(video_path)
                    st.success("✓ Model processing completed")
                    
                    # Step 2: Load tracks
                    st.write("🔄 Loading tracking data...")
                    tracks = load_json(TRACKS_FILE)
                    
                    if not tracks:
                        st.error("No tracks found after model processing.")
                        st.stop()
                    
                    # Step 3: ROI Mapping
                    st.write("🔄 Mapping tracks to ROIs...")
                    roi_mapper = ROIMapper()
                    mapped_tracks = roi_mapper.map_tracks(tracks)
                    st.success(f"✓ ROI Mapping completed ({len(mapped_tracks)} frames)")
                    
                    # Step 4: Event Detection
                    st.write("🔄 Generating events...")
                    event_engine = EventEngine()
                    events = event_engine.process(mapped_tracks)
                    st.success(f"✓ Events generated for {len(events)} persons")
                    
                    # Step 5: Timeline Generation
                    st.write("🔄 Generating timeline...")
                    timeline_generator = TimelineGenerator()
                    timeline = timeline_generator.generate(events)
                    st.success("✓ Timeline saved successfully")
                    
                    st.info("✅ Processing complete! View the timeline below.")
                    
                    # Mark processing as complete in session state
                    st.session_state.processing_complete = True
                    
                except Exception as e:
                    st.error(f"Error during processing: {str(e)}")
                    st.stop()
                
                finally:
                    # Clean up temp file (don't save uploaded video permanently)
                    if Path(video_path).exists():
                        Path(video_path).unlink()

# Only load and show timeline if processing has been completed in this session
if st.session_state.processing_complete:
timeline = load_json(TIMELINE_FILE)

if not timeline:
    st.info("👆 Upload a video above to get started, or run `python main.py` to process a video from the command line.")
    st.stop()
    
    # Show results section
    st.markdown("---")
    st.markdown("## 📊 Timeline Results")

# Show results section
st.markdown("---")
st.markdown("## 📊 Timeline Results")

persons = sorted(timeline.keys(), key=int)

# Person selection in main area
selected_person = st.selectbox(
    "Select Person to View Timeline",
    persons,
    key="person_selector"
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
    
    st.markdown("### 📅 Timeline")
    
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
    st.info("No events found for this person.")

# Sidebar for summary stats
    # Sidebar for summary stats
st.sidebar.markdown("---")
st.sidebar.header("Summary")
    st.sidebar.header("Summary")
st.sidebar.metric("Total Persons", len(persons))
st.sidebar.metric("Events for Selected Person", len(events))