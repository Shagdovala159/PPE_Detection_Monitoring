# import the require packages.
import cv2
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, \
    QLabel, QGridLayout, QScrollArea, QSizePolicy, QMessageBox
from PyQt5.QtGui import QPixmap, QIcon, QImage, QPalette
from PyQt5.QtCore import QThread, pyqtSignal, Qt, QEvent, QObject
from PyQt5 import QtCore
import sys
import numpy as np
import torch
import time
import os
model = torch.hub.load(r'yolov5', 'custom', path='yolov5/runs/train/exp2/weights/best.pt', source='local', force_reload=True, device='cpu')
# capture photo
output_folder = 'foto'  # Folder tujuan penyimpanan foto

# Buat folder tujuan jika belum ada
if not os.path.exists(output_folder):
    os.makedirs(output_folder)
class CaptureIpCameraFramesWorker(QThread):
    # Signal emitted when a new image or a new frame is ready.
    ImageUpdated = pyqtSignal(QImage)
    warningSignalhelm = pyqtSignal()
    warningSignalvest = pyqtSignal()

    def __init__(self, url) -> None:
        super(CaptureIpCameraFramesWorker, self).__init__()
        # Declare and initialize instance variables.
        self.url = url
        self.__thread_active = True
        self.fps = 0
        self.__thread_pause = False
        self.current_time = time.time()
        self.last_time = 0

    def run(self) -> None:
        # Capture video from a network stream.
        # model = torch.hub.load(r'yolov5', 'custom', path='yolov5/runs/train/exp/weights/best.pt', source='local', force_reload=True, device='cpu')
        cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
        # Get default video FPS.
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        print(self.fps)
        # If video capturing has been initialized already.q
        if cap.isOpened():
            # While the thread is active.
            while self.__thread_active:
                #
                if not self.__thread_pause:
                    self.last_time = time.time()
                    # Grabs, decodes and returns the next video frame.
                    ret, cv_img = cap.read()
                    resized_img = cv2.resize(cv_img, (640, 480))
                    results = model(resized_img)
                    frame = np.squeeze(results.render())
                    coor = results.xyxy[0]
                    rows = len(coor)
                    i = 0
                    while i < rows:
                        if coor[i][5].item() == 1:
                            print("terdeteksi no-helmet")
                            if self.last_time - self.current_time >= 15:
                                timestr = time.strftime("%m%d%H%M%S")
                                filename = f'foto_{timestr}.jpg'  # Nama file foto dengan format 'foto_counter.jpg'
                                file_path = os.path.join(output_folder, filename)
                                cv2.imwrite(file_path, np.squeeze(results.render()))
                                print(f"Foto {filename} diambil dan disimpan!")
                                self.warningSignalhelm.emit()
                                self.current_time = time.time()

                        if coor[i][5].item() == 2:
                            print("terdeteksi no-vest")
                            if self.last_time - self.current_time >= 15:
                                timestr = time.strftime("%m%d%H%M%S")
                                filename = f'foto_{timestr}.jpg'  # Nama file foto dengan format 'foto_counter.jpg'
                                file_path = os.path.join(output_folder, filename)
                                cv2.imwrite(file_path, np.squeeze(results.render()))
                                print(f"Foto {filename} diambil dan disimpan!")
                                self.warningSignalvest.emit()
                                self.current_time = time.time()
                    if ret:
                        # Get the frame height, width and channels.
                        height, width, channels = frame.shape
                        # Resize the frame to match the expected size.
                        # frame = cv2.resize(frame, (width, height))
                        # Calculate the number of bytes per line.
                        bytes_per_line = width * channels
                        # Convert image from BGR (cv2 default color format) to RGB (Qt default color format).
                        cv_rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                        # Convert the image to Qt format.
                        qt_rgb_image = QImage(cv_rgb_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
                        # Scale the image.
                        # NOTE: consider removing the flag Qt.KeepAspectRatio as it will crash Python on older Windows machines
                        # If this is the case, call instead: qt_rgb_image.scaled(1280, 720)
                        qt_rgb_image_scaled = qt_rgb_image.scaled(1280, 720, Qt.KeepAspectRatio)  # 720p
                        # qt_rgb_image_scaled = qt_rgb_image.scaled(1920, 1080, Qt.KeepAspectRatio)
                        # Emit this signal to notify that a new image or frame is available.
                        self.ImageUpdated.emit(qt_rgb_image_scaled)
                    else:
                        break
        # When everything done, release the video capture object.
        cap.release()
        # Tells the thread's event loop to exit with return code 0 (success).
        self.quit()

    def stop(self) -> None:
        self.__thread_active = False

    def pause(self) -> None:
        self.__thread_pause = True

    def unpause(self) -> None:
        self.__thread_pause = False


class MainWindow(QMainWindow):

    def __init__(self) -> None:
        super(MainWindow, self).__init__()

        self.url_1 = "http://158.58.130.148:80/mjpg/video.mjpg"
        self.url_2 = "http://195.196.36.242/mjpg/video.mjpg"
        self.url_3 = "http://camera.buffalotrace.com/mjpg/video.mjpg"
        self.url_4 = "http://webcam.mchcares.com/mjpg/video.mjpg?timestamp=1566232173730"
        # rtsp://<Username>:<Password>@<IP Address>:<Port>/cam/realmonitor?channel=1&subtype=0
        # self.url_1 = "http://158.58.130.148:80/mjpg/video.mjpg"
        # self.url_2 = "http://camera.buffalotrace.com/mjpg/video.mjpg"
        # self.url_3 = "http://tamperehacklab.tunk.org:38001/nphMotionJpeg?Resolution=640x480&Quality=Clarity"
        # self.url_4 = "http://47.51.131.147/-wvhttp-01-/GetOneShot?image_size=1280x720&frame_count=1000000000"

        # Dictionary to keep the state of a camera. The camera state will be: Normal or Maximized.
        self.list_of_cameras_state = {}

        # Create an instance of a QLabel class to show camera 1.
        self.camera_1 = QLabel()
        self.camera_1.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_1.setScaledContents(True)
        self.camera_1.installEventFilter(self)
        self.camera_1.setObjectName("Camera_1")
        self.list_of_cameras_state["Camera_1"] = "Normal"

        # Create an instance of a QScrollArea class to scroll camera 1 image.
        self.QScrollArea_1 = QScrollArea()
        self.QScrollArea_1.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_1.setWidgetResizable(True)
        self.QScrollArea_1.setWidget(self.camera_1)

        # Create an instance of a QLabel class to show camera 2.
        self.camera_2 = QLabel()
        self.camera_2.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_2.setScaledContents(True)
        self.camera_2.installEventFilter(self)
        self.camera_2.setObjectName("Camera_2")
        self.list_of_cameras_state["Camera_2"] = "Normal"

        # Create an instance of a QScrollArea class to scroll camera 2 image.
        self.QScrollArea_2 = QScrollArea()
        self.QScrollArea_2.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_2.setWidgetResizable(True)
        self.QScrollArea_2.setWidget(self.camera_2)

        # Create an instance of a QLabel class to show camera 3.
        self.camera_3 = QLabel()
        self.camera_3.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_3.setScaledContents(True)
        self.camera_3.installEventFilter(self)
        self.camera_3.setObjectName("Camera_3")
        self.list_of_cameras_state["Camera_3"] = "Normal"

        # Create an instance of a QScrollArea class to scroll camera 3 image.
        self.QScrollArea_3 = QScrollArea()
        self.QScrollArea_3.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_3.setWidgetResizable(True)
        self.QScrollArea_3.setWidget(self.camera_3)

        # Create an instance of a QLabel class to show camera 4.
        self.camera_4 = QLabel()
        self.camera_4.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.camera_4.setScaledContents(True)
        self.camera_4.installEventFilter(self)
        self.camera_4.setObjectName("Camera_4")
        self.list_of_cameras_state["Camera_4"] = "Normal"

        # Create an instance of a QScrollArea class to scroll camera 4 image.
        self.QScrollArea_4 = QScrollArea()
        self.QScrollArea_4.setBackgroundRole(QPalette.Dark)
        self.QScrollArea_4.setWidgetResizable(True)
        self.QScrollArea_4.setWidget(self.camera_4)

        # Set the UI elements for this Widget class.
        self.__SetupUI()

        # Create an instance of CaptureIpCameraFramesWorker.
        self.CaptureIpCameraFramesWorker_1 = CaptureIpCameraFramesWorker(self.url_1)
        self.CaptureIpCameraFramesWorker_1.ImageUpdated.connect(lambda image: self.ShowCamera1(image))
        self.CaptureIpCameraFramesWorker_1.warningSignalhelm.connect(self.showWarninghelm)
        self.CaptureIpCameraFramesWorker_1.warningSignalvest.connect(self.showWarningvest)
        # Create an instance of CaptureIpCameraFramesWorker.
        self.CaptureIpCameraFramesWorker_2 = CaptureIpCameraFramesWorker(self.url_2)
        self.CaptureIpCameraFramesWorker_2.ImageUpdated.connect(lambda image: self.ShowCamera2(image))
        self.CaptureIpCameraFramesWorker_2.warningSignalhelm.connect(self.showWarninghelm)
        self.CaptureIpCameraFramesWorker_2.warningSignalvest.connect(self.showWarningvest)

        # Create an instance of CaptureIpCameraFramesWorker.
        self.CaptureIpCameraFramesWorker_3 = CaptureIpCameraFramesWorker(self.url_3)
        self.CaptureIpCameraFramesWorker_3.ImageUpdated.connect(lambda image: self.ShowCamera3(image))
        self.CaptureIpCameraFramesWorker_3.warningSignalhelm.connect(self.showWarninghelm)
        self.CaptureIpCameraFramesWorker_3.warningSignalvest.connect(self.showWarningvest)

        # Create an instance of CaptureIpCameraFramesWorker.
        self.CaptureIpCameraFramesWorker_4 = CaptureIpCameraFramesWorker(self.url_4)
        self.CaptureIpCameraFramesWorker_4.ImageUpdated.connect(lambda image: self.ShowCamera4(image))
        self.CaptureIpCameraFramesWorker_4.warningSignalhelm.connect(self.showWarninghelm)
        self.CaptureIpCameraFramesWorker_4.warningSignalvest.connect(self.showWarningvest)
        # Start the thread getIpCameraFrameWorker_1.
        self.CaptureIpCameraFramesWorker_1.start()

        # Start the thread getIpCameraFrameWorker_2.
        self.CaptureIpCameraFramesWorker_2.start()

        # Start the thread getIpCameraFrameWorker_3.
        self.CaptureIpCameraFramesWorker_3.start()

        # Start the thread getIpCameraFrameWorker_4.
        self.CaptureIpCameraFramesWorker_4.start()

    def __SetupUI(self) -> None:
        # Create an instance of a QGridLayout layout.
        grid_layout = QGridLayout()
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.addWidget(self.QScrollArea_1, 0, 0)
        grid_layout.addWidget(self.QScrollArea_2, 0, 1)
        grid_layout.addWidget(self.QScrollArea_3, 1, 0)
        grid_layout.addWidget(self.QScrollArea_4, 1, 1)

        # Create a widget instance.
        self.widget = QWidget(self)
        self.widget.setLayout(grid_layout)

        # Set the central widget.
        self.setCentralWidget(self.widget)
        self.setMinimumSize(800, 600)
        self.showMaximized()
        self.setStyleSheet("QMainWindow {background: 'black';}")
        self.setWindowIcon(QIcon(QPixmap("camera_2.png")))
        # Set window title.
        self.setWindowTitle("IP Camera System")

    @QtCore.pyqtSlot()
    def ShowCamera1(self, frame: QImage) -> None:
        self.camera_1.setPixmap(QPixmap.fromImage(frame))

    @QtCore.pyqtSlot()
    def ShowCamera2(self, frame: QImage) -> None:
        self.camera_2.setPixmap(QPixmap.fromImage(frame))

    @QtCore.pyqtSlot()
    def ShowCamera3(self, frame: QImage) -> None:
        self.camera_3.setPixmap(QPixmap.fromImage(frame))

    @QtCore.pyqtSlot()
    def ShowCamera4(self, frame: QImage) -> None:
        self.camera_4.setPixmap(QPixmap.fromImage(frame))

    # Override method for class MainWindow.
    def eventFilter(self, source: QObject, event: QEvent) -> bool:
        """
        Method to capture the events for objects with an event filter installed.
        :param source: The object for whom an event took place.
        :param event: The event that took place.
        :return: True if event is handled.
        """
        #
        if event.type() == QtCore.QEvent.MouseButtonDblClick:
            if source.objectName() == 'Camera_1':
                #
                if self.list_of_cameras_state["Camera_1"] == "Normal":
                    self.QScrollArea_2.hide()
                    self.QScrollArea_3.hide()
                    self.QScrollArea_4.hide()
                    self.list_of_cameras_state["Camera_1"] = "Maximized"
                else:
                    self.QScrollArea_2.show()
                    self.QScrollArea_3.show()
                    self.QScrollArea_4.show()
                    self.list_of_cameras_state["Camera_1"] = "Normal"
            elif source.objectName() == 'Camera_2':
                #
                if self.list_of_cameras_state["Camera_2"] == "Normal":
                    self.QScrollArea_1.hide()
                    self.QScrollArea_3.hide()
                    self.QScrollArea_4.hide()
                    self.list_of_cameras_state["Camera_2"] = "Maximized"
                else:
                    self.QScrollArea_1.show()
                    self.QScrollArea_3.show()
                    self.QScrollArea_4.show()
                    self.list_of_cameras_state["Camera_2"] = "Normal"
            elif source.objectName() == 'Camera_3':
                #
                if self.list_of_cameras_state["Camera_3"] == "Normal":
                    self.QScrollArea_1.hide()
                    self.QScrollArea_2.hide()
                    self.QScrollArea_4.hide()
                    self.list_of_cameras_state["Camera_3"] = "Maximized"
                else:
                    self.QScrollArea_1.show()
                    self.QScrollArea_2.show()
                    self.QScrollArea_4.show()
                    self.list_of_cameras_state["Camera_3"] = "Normal"
            elif source.objectName() == 'Camera_4':
                #
                if self.list_of_cameras_state["Camera_4"] == "Normal":
                    self.QScrollArea_1.hide()
                    self.QScrollArea_2.hide()
                    self.QScrollArea_3.hide()
                    self.list_of_cameras_state["Camera_4"] = "Maximized"
                else:
                    self.QScrollArea_1.show()
                    self.QScrollArea_2.show()
                    self.QScrollArea_3.show()
                    self.list_of_cameras_state["Camera_4"] = "Normal"
            else:
                return super(MainWindow, self).eventFilter(source, event)
            return True
        else:
            return super(MainWindow, self).eventFilter(source, event)

    # Overwrite method closeEvent from class QMainWindow.
    def closeEvent(self, event) -> None:
        # If thread getIpCameraFrameWorker_1 is running, then exit it.
        if self.CaptureIpCameraFramesWorker_1.isRunning():
            self.CaptureIpCameraFramesWorker_1.quit()
        # If thread getIpCameraFrameWorker_2 is running, then exit it.
        if self.CaptureIpCameraFramesWorker_2.isRunning():
            self.CaptureIpCameraFramesWorker_2.quit()
        # If thread getIpCameraFrameWorker_3 is running, then exit it.
        if self.CaptureIpCameraFramesWorker_3.isRunning():
            self.CaptureIpCameraFramesWorker_3.quit()
        # If thread getIpCameraFrameWorker_4 is running, then exit it.
        if self.CaptureIpCameraFramesWorker_4.isRunning():
            self.CaptureIpCameraFramesWorker_4.quit()
        # Accept the event
        event.accept()

    def showWarninghelm(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("No-vest terdeteksi")
        msg.setWindowTitle("Warning")
        msg.exec_()

    def showWarningvest(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)
        msg.setText("No-vest terdeteksi")
        msg.setWindowTitle("Warning")
        msg.exec_()

def main() -> None:
    # Create a QApplication object. It manages the GUI application's control flow and main settings.
    # It handles widget specific initialization, finalization.
    # For any GUI application using Qt, there is precisely one QApplication object
    app = QApplication(sys.argv)
    # Create an instance of the class MainWindow.
    window = MainWindow()
    # Show the window.
    window.show()
    # Start Qt event loop.
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()