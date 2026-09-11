from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import psycopg2
import psycopg2.extras

app = FastAPI(title="Urban Intelligence API")

# These match model.names from your video_test.py output:
# {0: 'D00', 1: 'D20', 2: 'D40', 3: 'D44', 4: 'autorickshaw', 5: 'bicycle',
#  6: 'bus', 7: 'car', 8: 'motorcycle', 9: 'truck'}
VEHICLE_CLASSES = {"autorickshaw", "bicycle", "bus", "car", "motorcycle", "truck"}
DAMAGE_CLASSES = {"d00", "d20", "d40", "d44"}

# Human-readable labels for the RDD2022 damage codes — use this to relabel
# class_name before sending it to the frontend, so the map popup says
# "Pothole" instead of "D40"
DAMAGE_LABELS = {
    "d00": "Longitudinal Crack",
    "d20": "Alligator Crack",
    "d40": "Pothole",
    "d44": "White Line / Paint Blur",
}


def get_conn():
    return psycopg2.connect(dbname="postgres")


@app.get("/api/summary")
def get_summary():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT class_name, COUNT(*) AS count FROM detections GROUP BY class_name;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return {"counts": rows}


@app.get("/api/route")
def get_route():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT lat, lon FROM positions ORDER BY frame_number;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [[row["lat"], row["lon"]] for row in rows]


@app.get("/api/vehicles")
def get_vehicles():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "SELECT id, frame_number, class_name, confidence, lat, lon "
        "FROM detections WHERE LOWER(class_name) = ANY(%s) ORDER BY frame_number;",
        (list(VEHICLE_CLASSES),),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@app.get("/api/damage")
def get_damage():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        "SELECT id, frame_number, class_name, confidence, lat, lon "
        "FROM detections WHERE LOWER(class_name) = ANY(%s) ORDER BY frame_number;",
        (list(DAMAGE_CLASSES),),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    for row in rows:
        row["class_name"] = DAMAGE_LABELS.get(row["class_name"].lower(), row["class_name"])
    return rows


# Serves index.html / script.js / style.css directly — visit http://localhost:8000
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
