import torch
from matplotlib import pyplot as plt
import time
import numpy as np
import cv2
import os
model = torch.hub.load(r'yolov5', 'custom', path='yolov5/runs/train/exp/weights/best.pt', source='local')
cap = cv2.VideoCapture(0)
current_time = time.time()

# capture photo
output_folder = 'foto'  # Folder tujuan penyimpanan foto

# Buat folder tujuan jika belum ada
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

counter = 1  # Counter untuk nama file

while cap.isOpened():
    ret, frame = cap.read()

    # Make detections
    results = model(frame)

    cv2.imshow('YOLO', np.squeeze(results.render()))
    last_time = time.time()
    # get class
    if last_time - current_time >= 3:
        coor = results.xyxy[0]
        rows = len(coor)
        i=0
        while i < rows:
            print(coor[i][5].item())
            if coor[i][5].item() == 4:
                print("ada vest")
                filename = f'foto_{counter}.jpg'  # Nama file foto dengan format 'foto_counter.jpg'
                file_path = os.path.join(output_folder, filename)
                cv2.imwrite(file_path, np.squeeze(results.render()))
                print(f"Foto {filename} diambil dan disimpan!")
                counter += 1
            i += 1
        print("sudah 3 detik")
        current_time = time.time()

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()