from ultralytics import YOLO


model = YOLO("/home/sureshsecond/SIH26/RDD_IDD_1050/runs/detect/train-6/weights/best.pt")

# model.predict("./sample_images/India_007550.jpg",conf=0.20,imgsz=640,device="cpu",verbose=False,save=True, show=False)
# model.predict("./sample_images/India_004224.jpg",conf=0.20,imgsz=640,device="cpu",verbose=False,save=True, show=False)
# model.predict("./sample_images/India_003774.jpg",conf=0.20,imgsz=640,device="cpu",verbose=False,save=True, show=False)

# good after some time
# model.predict("./sample_videos/Driving In India.mp4",conf=0.30,imgsz=720,device="cpu",verbose=False,save=True, show=False)
# model.predict("./sample_videos/111_10-07-2023.mp4",conf=0.30,imgsz=640,device="cpu",verbose=False,save=True, show=False)
#model.predict("./sample_videos/best1.mp4",conf=0.30,imgsz=640,device="cpu",verbose=False,save=True, show=False, stream=True)
#model.predict("./sample_videos/best2.mp4",conf=0.30,imgsz=640,device="cpu",verbose=False,save=True, show=False, stream=True)
model.predict("../sample_videos/best1.mp4",conf=0.10,imgsz=640,device="cpu",verbose=False,save=True, show=False, stream=False)