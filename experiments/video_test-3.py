from ultralytics import YOLO
import cv2


model = YOLO("/home/sureshsecond/SIH26/RDD_IDD_1050/runs/detect/train-3/weights/best.pt")

video_path = "./sample_videos/vehicle-counting.mp4"
cap = cv2.VideoCapture(video_path)

while True:
    res, frame = cap.read()
    if not res:
        break
    results = model.predict(frame,conf=0.20,imgsz=640,device="cpu",verbose=False,save=True, show=False)
    print(results[0].names)
    result = results[0]
    # detected clsses
    class_ids = result.boxes.cls
    print(class_ids) # I will give these to website
    
    if class_ids is not None:
        for class_id in class_ids:
            class_id = int(class_id)
            class_name = result.names[class_id]
            print(class_id,class_name)

    break
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break



cap.release()
cv2.destroyAllWindows()