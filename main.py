import cv2
import psycopg2
from ultralytics import YOLO

# Connect via local Unix socket without host/password
conn = psycopg2.connect(dbname="postgres")
cursor = conn.cursor()

# Ensure target table exists (lat/lon added for map plotting)
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS detections (
        id SERIAL PRIMARY KEY,
        video_name TEXT NOT NULL,
        frame_number INTEGER NOT NULL,
        class_id INTEGER NOT NULL,
        class_name TEXT NOT NULL,
        confidence REAL NOT NULL,
        lat REAL,
        lon REAL
    );
"""
)
conn.commit()

# If the table already existed from before (without lat/lon), add the columns
cursor.execute("ALTER TABLE detections ADD COLUMN IF NOT EXISTS lat REAL;")
cursor.execute("ALTER TABLE detections ADD COLUMN IF NOT EXISTS lon REAL;")
conn.commit()

# Logs the bus's simulated position for every processed frame, regardless of
# whether anything was detected — this is what the frontend draws the route
# line from, so the line actually matches where the dots come from.
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS positions (
        id SERIAL PRIMARY KEY,
        video_name TEXT NOT NULL,
        frame_number INTEGER NOT NULL,
        lat REAL NOT NULL,
        lon REAL NOT NULL
    );
"""
)
conn.commit()

# Load model
model = YOLO("./runs/detect/train-6/weights/best.pt")

video_path = "./sample_videos/best1.mp4"
cap = cv2.VideoCapture(video_path)

# Clear old entries for this video before inserting new ones
cursor.execute("DELETE FROM detections WHERE video_name = %s;", (video_path,))
cursor.execute("DELETE FROM positions WHERE video_name = %s;", (video_path,))
conn.commit()

insert_query = """
    INSERT INTO detections (video_name, frame_number, class_id, class_name, confidence, lat, lon)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
"""

insert_position_query = """
    INSERT INTO positions (video_name, frame_number, lat, lon)
    VALUES (%s, %s, %s, %s);
"""

# ------------------------------------------------------------------
# Simulated GPS — this is a video prototype with no real GPS logger.
# Each processed frame steps forward by a fixed amount so points are
# spaced out clearly on the map instead of clustering together.
# Raise/lower STEP_LAT and STEP_LON until the spacing looks right at
# your demo zoom level.
# ------------------------------------------------------------------
START_LAT, START_LON = 15.5150, 80.0250
STEP_LAT, STEP_LON = 0.0009, 0.0009


def get_position(step_index):
    lat = START_LAT - step_index * STEP_LAT
    lon = START_LON + step_index * STEP_LON
    return lat, lon


# Process every 5th frame
frame_skip = 5
frame_count = 0
processed_frames = 0

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
        show=False,
    )

    processed_frames += 1
    result = results[0]

    # Position for this processed frame — every detection found in this
    # frame shares the same simulated GPS point
    lat, lon = get_position(processed_frames)

    # Log the bus's position for this frame regardless of detections —
    # this is what builds the real route line
    cursor.execute(insert_position_query, (video_path, frame_count, lat, lon))
    conn.commit()

    # Insert detections into database
    if result.boxes is not None and len(result.boxes) > 0:
        class_ids = result.boxes.cls.cpu().numpy()
        confidences = result.boxes.conf.cpu().numpy()

        for class_id, conf in zip(class_ids, confidences):
            cursor.execute(
                insert_query,
                (
                    video_path,
                    frame_count,
                    int(class_id),
                    result.names[int(class_id)],
                    float(conf),
                    lat,
                    lon,
                ),
            )

        conn.commit()

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()

cursor.close()
conn.close()
