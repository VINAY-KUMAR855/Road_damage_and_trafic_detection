from ultralytics import YOLO
import cv2
import time

# Load model
model = YOLO("../runs/detect/train-6/weights/best.pt")

video_path = "../sample_videos/best1.mp4"

cap = cv2.VideoCapture(video_path)

# Video FPS
# fps = cap.get(cv2.CAP_PROP_FPS)

# print("Video FPS:", fps)

# Process every 3rd frame
frame_skip = 3

frame_count = 0
processed_frames = 0

start_time = time.time()

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame_count += 1

    # Skip frames
    if frame_count % frame_skip != 0:
        continue

    # YOLO inference
    results = model.predict(
        frame,
        conf=0.20,
        imgsz=640,
        device="cpu",      
        verbose=False,
        save=False,
        show=False
    )
    # print(results[0].names)
    processed_frames += 1

    # Detected classes
    class_ids = results[0].boxes.cls

    print(class_ids)

    break 

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break


# end_time = time.time()

# total_time = end_time - start_time

# print("\n----------------------------")
# print("Total video frames:", frame_count)
# print("Processed frames:", processed_frames)
# print(f"Total processing time: {total_time:.2f} seconds")
# print(f"Processing time: {total_time / 60:.2f} minutes")
# print("----------------------------")

cap.release()
cv2.destroyAllWindows()