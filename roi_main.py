from core.roi_creator import ROICreator

creator = ROICreator(
    image_path="processed_video/frames/frame_00000.jpg",
    output_file="data/roi.json"
)

creator.run()