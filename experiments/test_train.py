from ultralytics import YOLO
# import cv2


model = YOLO("/home/sureshsecond/SIH26/RDD_IDD_1050/runs/detect/train/weights/best.pt")

# results = model.predict("./sample_images/India_007550.jpg",conf=0.10,imgsz=640,device="cpu",verbose=False,save=True, show=False)
model.predict("./sample_videos/Driving In India.mp4",conf=0.25,imgsz=640,device="cpu",verbose=False,save=True, show=False)

# annotated = results[0].plot()
# cv2.imshow("res",annotated)

# cv2.waitKey(0)
# cv2.destroyAllWindows()