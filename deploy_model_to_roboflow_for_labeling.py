from roboflow import Roboflow

rf = Roboflow(api_key="mbvuB9uRXXXX0UmuenjO")
workspace = rf.workspace()

workspace.deploy_model(
  model_type="yolov8",
  model_path="./runs/detect/train-3/",
  project_ids=["rdd-india-1pbjf"],
  model_name="my-custom-model"
)
