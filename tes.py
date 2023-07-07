import torch
from matplotlib import pyplot as plt
import numpy as np
import cv2
model = torch.hub.load(r'yolov5', 'custom', path='yolov5/runs/train/exp/weights/best.pt', source='local')
cap = cv2.VideoCapture(0)
while cap.isOpened():
    ret, frame = cap.read()

    # Make detections
    results = model(frame)

    cv2.imshow('YOLO', np.squeeze(results.render()))
    coor = results.xyxy[0]
    rows = len(coor)
    # print(coor)
    # print(rows)
    i=0
    while i < rows:
        print(coor[i][5].item())
        i += 1
    print("done")
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()