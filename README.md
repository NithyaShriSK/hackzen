# Hackzen: Human Activity Timeline Generator

Hackzen is a computer-vision project that turns retail/store video into a structured activity timeline. It detects people in a video, assigns each detection to a store region of interest (ROI), converts movement into meaningful events such as entering the store, browsing a department, visiting checkout, and exiting, then saves the result as a timeline that can be viewed in a Streamlit dashboard.

The repository also includes YOLO training artifacts for a custom retail detection model. The main runtime pipeline in this codebase consumes tracking data from JSON, while the saved training runs document how the detector was fine-tuned.

## What The Project Does

The workflow is designed for retail analytics and customer journey tracking:

1. A video is preprocessed into frames and metadata.
2. Object tracking data is loaded from JSON.
3. Each bounding box is mapped to a store zone using polygon ROIs.
4. Zone transitions are converted into business events.
5. Events are aggregated into a per-person timeline and written to disk.
6. The timeline is displayed in a small Streamlit dashboard.

Example events include:

- Entered Store
- Browsing
- Entered Checkout
- Exited Store

## Tech Stack

This project uses:

- Python
- OpenCV for video preprocessing and ROI drawing
- Shapely for point-in-polygon checks
- Pandas for dashboard tables
- Plotly and Streamlit for the visualization layer
- JSON files for ROI, track, and timeline storage
- Ultralytics YOLO for object detection and tracking
- Supervision for video processing utilities
- Ollama for AI model integration

## How The Pipeline Works

### 1. Model-based tracking

`model.py` runs YOLO-based object detection and tracking on the input video. It uses:
- A custom product detection model (`runs/detect/train-2/weights/best.pt`)
- A pre-trained people detection model (`yolo11m.pt`)
- Advanced time-based identity memory to maintain consistent person tracking across frames
- Outputs tracking data to `data/tracks.json` and an annotated video to `retail_tracked_output.mp4`

### 2. ROI creation

`core/roi_creator.py` provides a simple OpenCV-based annotation tool. You click points on a frame to draw polygons and save named regions into `data/roi.json`.

### 3. ROI mapping

`core/roi_mapper.py` loads the polygon ROIs and checks where each bounding-box center falls. If the center lands inside a polygon, the track is assigned that zone. If not, it is marked as Outside.

### 4. Event generation

`core/event_engine.py` watches zone transitions per person and converts them into semantic events. The current logic focuses on store entry, exit, checkout visits, and general movement between business zones.

### 5. Timeline generation

`core/timeline.py` sorts and deduplicates events per person, then saves the final timeline to `data/timeline.json`.

### 6. Dashboard

`dashboard/app.py` loads the saved timeline and renders it in a Streamlit app so the activity of each person can be reviewed quickly.

## Model Fine-Tuning

The repository includes saved Ultralytics training configs under `runs/detect/`. From those artifacts, the detector was fine-tuned with the following setup:

- Base model: `yolo11m.pt`
- Task: detection
- Dataset config: `data.yaml`
- Epochs: 50 for the main run
- Batch size: 16
- Image size: 640
- Pretrained weights enabled: yes
- Optimizer: auto
- Mixed precision: enabled
- Deterministic training: enabled

There is also a shorter secondary run recorded in `runs/detect/train-2/args.yaml` with:

- Epochs: 3
- Batch size: 32
- Image size: 320

This repository does not currently include the training script or the `data.yaml` file itself, so the README documents the saved configuration rather than claiming an exact reproduction pipeline. The important idea is transfer learning: starting from the pretrained YOLO11m checkpoint and adapting it to the custom retail dataset.

## Project Structure

- `main.py` runs the end-to-end preprocessing, mapping, event generation, and timeline export flow.
- `roi_main.py` launches the ROI annotation tool.
- `core/` contains the main logic for preprocessing, ROI handling, event detection, timeline generation, and shared helpers.
- `dashboard/` contains the Streamlit UI.
- `data/` stores ROI definitions, track data, and generated timelines.
- `processed_video/` stores extracted frames and video metadata.
- `runs/` stores YOLO training results and configuration snapshots.

## Setup

### 1. Create and activate a virtual environment

Use your preferred Python environment manager. If you want to reuse the included environment layout, activate the local virtual environment first.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Prepare your input video

Place a store or retail video in the project root directory and update the `video_path` variable in `main.py` if needed. The project includes sample videos (`sample.mp4`, `sample1.mp4`) for testing.

The video path is passed to the YOLO model which processes it and saves the tracking data to `data/tracks.json`.

## Usage

### Option 1: Using the Streamlit App (Recommended)

```bash
streamlit run dashboard/app.py
```

The Streamlit app provides a user-friendly interface to:

1. **Upload a video** - Use the file uploader in the sidebar to upload your video (mp4, avi, mov)
2. **Process the video** - Click "Process Video" to run the complete pipeline:
   - YOLO model detection and tracking
   - ROI mapping
   - Event generation
   - Timeline generation
3. **View the timeline** - Browse the generated timeline for each tracked person

### Option 2: Using the Command Line

```bash
python main.py
```

This will:

- Run YOLO model to generate tracking data from the input video (specified in `main.py`)
- Save annotated video to `retail_tracked_output.mp4`
- Save tracking data to `data/tracks.json`
- Load tracks and map them to ROIs
- Generate events
- Save `data/timeline.json`

### Define ROIs

```bash
python roi_main.py
```

Use the mouse to draw polygons on the frame, press Enter to save each ROI, and press `S` or `Q` to write `data/roi.json`.

### Open the dashboard

```bash
streamlit run dashboard/app.py
```

The dashboard will show the generated timeline for each tracked person.

## Output Files

- `processed_video/frames/` stores extracted image frames
- `processed_video/metadata/video_info.json` stores video metadata
- `data/roi.json` stores ROI polygons
- `data/timeline.json` stores the final per-person activity timeline

## Notes

- The current event engine is rule-based, so it can be extended with more business logic such as dwell-time thresholds or queue detection.
- The repo already contains example data in `data/` so you can inspect the expected JSON format immediately.
- If you want full model reproducibility, add the missing `data.yaml` and the exact training command used for the YOLO run.

