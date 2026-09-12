import psycopg2

conn = psycopg2.connect(dbname="postgres")
cursor = conn.cursor()

cursor.execute(
    '''
    SELECT DISTINCT VIDEO_NAME FROM detections
'''
)
# cursor.execute(
#     '''
#     DELETE FROM detections
# '''
# )
# conn.commit()

frames = cursor.fetchall()

for frame in frames:
    print(frame)

