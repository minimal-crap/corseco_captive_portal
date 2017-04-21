import numpy as np
import cv2
import redis
import time
import random
import requests as rq


redis_client = redis.StrictRedis()
capture_instance = cv2.VideoCapture(0)

while True:
    ret, rfame = capture_instance.read()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    send_image_to_api = redis_client.get("start_camera")
    if send_image_to_api == 'true':
        file_name = random.randint(100000,999999)
        file_name = "image_{}.jpg".format(file_name)
        cv2.imwrite(file_name, gray)

    cv2.imshow('frame', gray)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture_instance.release()
cv2.destroyAllWindows()
