# model.py
import os
import cv2
import json
import numpy as np
import supervision as sv
from ultralytics import YOLO
from tqdm import tqdm

def model_run(INPUT_VIDEO):
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    OUTPUT_VIDEO = "retail_tracked_output.mp4"
    OUTPUT_JSON = "data/tracks.json"

    PRODUCT_WEIGHTS = "runs/detect/train-2/weights/best.pt"
    PEOPLE_WEIGHTS = "yolo11m.pt"

    cap = cv2.VideoCapture(INPUT_VIDEO)
    if not cap.isOpened():
        print(f"Error: Could not open input video file: {INPUT_VIDEO}")
        return None

    video_info = sv.VideoInfo.from_video_path(video_path=INPUT_VIDEO)
    total_frames = video_info.total_frames
    fps = video_info.fps

    box_annotator = sv.BoxAnnotator(thickness=2)
    label_annotator = sv.LabelAnnotator(text_scale=0.4, text_thickness=1)

    print("Loading models onto GPU VRAM...")
    product_model = YOLO(PRODUCT_WEIGHTS).to('cuda')
    people_model = YOLO(PEOPLE_WEIGHTS).to('cuda')

    track_history = {}  
    id_mapping_registry = {}    
    MAX_MEMORY_FRAMES = 10.0 * fps  
    MAX_DISTANCE_THRESHOLD = 1500.0  

    json_output_data = {
        "metadata": {
            "input_video": INPUT_VIDEO,
            "total_frames": total_frames,
            "fps": fps
        },
        "frames": []
    }

    pbar = tqdm(total=total_frames, desc="Processing Video Frames", unit="frame")
    frame_idx = 0

    with sv.VideoSink(target_path=OUTPUT_VIDEO, video_info=video_info) as video_sink:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            product_results = product_model.predict(
                source=frame, device=0, imgsz=640, conf=0.25, iou=0.60, max_det=1000, verbose=False
            )
            prod_detections = sv.Detections.from_ultralytics(product_results[0])
            if prod_detections.tracker_id is None:
                prod_detections.tracker_id = np.array([None] * len(prod_detections))
            
            people_results = people_model.track(
                source=frame, tracker="botsort.yaml", persist=True, device=0, imgsz=640, conf=0.30, classes=[0], verbose=False
            )
            people_detections = sv.Detections.from_ultralytics(people_results[0])
            
            if len(people_detections) > 1:
                people_detections = people_detections.with_nms(threshold=0.5)
                
            if people_detections.tracker_id is None:
                people_detections.tracker_id = np.array([None] * len(people_detections))
            
            fixed_tracker_ids = []
            for i in range(len(people_detections)):
                tid = people_detections.tracker_id[i]
                if tid is None:
                    fixed_tracker_ids.append(None)
                    continue
                    
                bbox = people_detections.xyxy[i]
                cx = (bbox[0] + bbox[2]) / 2.0
                cy = (bbox[1] + bbox[3]) / 2.0
                current_center = (cx, cy)
                
                if tid in id_mapping_registry:
                    resolved_id = id_mapping_registry[tid]
                else:
                    resolved_id = tid
                    min_dist = float('inf')
                    matched_historical_id = None
                    
                    for hist_id, data in list(track_history.items()):
                        frame_gap = frame_idx - data["frame_idx"]
                        if frame_gap <= MAX_MEMORY_FRAMES:
                            hist_center = data["center"]
                            dist = np.sqrt((cx - hist_center[0])**2 + (cy - hist_center[1])**2)
                            
                            if dist < min_dist and dist < MAX_DISTANCE_THRESHOLD:
                                min_dist = dist
                                matched_historical_id = hist_id
                    
                    if matched_historical_id is not None and matched_historical_id != tid:
                        resolved_id = matched_historical_id
                        id_mapping_registry[tid] = resolved_id
                        
                        if resolved_id in track_history:
                            del track_history[resolved_id]
                
                track_history[resolved_id] = {"center": current_center, "frame_idx": frame_idx}
                fixed_tracker_ids.append(resolved_id)
                
            if len(people_detections) > 0:
                people_detections.tracker_id = np.array(fixed_tracker_ids)
            
            combined_detections = sv.Detections.merge([prod_detections, people_detections])
            
            labels = []
            frame_detections_log = []
            
            for i in range(len(combined_detections)):
                confidence = float(combined_detections.confidence[i])
                bbox = combined_detections.xyxy[i].tolist()
                track_id_val = combined_detections.tracker_id[i]
                
                if track_id_val is not None and not (isinstance(track_id_val, float) and np.isnan(track_id_val)):
                    track_id = int(track_id_val)
                    labels.append(f"Person #{track_id} ({confidence:.2f})")
                    
                    frame_detections_log.append({
                        "class": "person",
                        "track_id": track_id,
                        "confidence": round(confidence, 4),
                        "bbox": [round(coord, 2) for coord in bbox]
                    })
                else:
                    labels.append(f"Product ({confidence:.2f})")
                    
                    frame_detections_log.append({
                        "class": "product",
                        "track_id": None,
                        "confidence": round(confidence, 4),
                        "bbox": [round(coord, 2) for coord in bbox]
                    })
            
            json_output_data["frames"].append({
                "frame_index": frame_idx,
                "timestamp_seconds": round(frame_idx / fps, 2),
                "detections_count": len(frame_detections_log),
                "objects": frame_detections_log
            })
            
            annotated_frame = box_annotator.annotate(scene=frame.copy(), detections=combined_detections)
            annotated_frame = label_annotator.annotate(scene=annotated_frame, detections=combined_detections, labels=labels)
            
            video_sink.write_frame(frame=annotated_frame)
            pbar.update(1)
            frame_idx += 1

    cap.release()
    pbar.close()

    with open(OUTPUT_JSON, "w") as json_file:
        json.dump(json_output_data, json_file, indent=4)

    return OUTPUT_JSON