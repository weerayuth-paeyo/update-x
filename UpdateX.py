import json
import os
import sys
from time import sleep
import requests
from PyQt5 import QtWidgets, uic
import zipfile

from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

import subprocess

from PyQt5.QtWidgets import QApplication


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()  # Call the inherited classes __init__ method
        uic.loadUi('Update_X.ui', self)  # Load the .ui file
        self.progressBar.setValue(0)
        self.pushButton.hide()
        self.label_process.setText("")
        self.label_file.setText("")
        self.show()

        self.file_name = "new_update.zip"

        self.thread = progressDownload(self.file_name)
        self.thread.data_bar.connect(self.updateBar)
        self.thread.start()

        self.pushButton.clicked.connect(lambda: self.close())

    def close(self):
        self.destroy()
        QApplication.closeAllWindows()

    @pyqtSlot(object)
    def updateBar(self, data_bar):
        if data_bar[0] == 0 and data_bar[1] == "finish" and data_bar[2] == "กำลังดาวน์โหลดไฟล์":
            self.thread = progressUpdateBar(self.file_name)
            self.thread.data_bar.connect(self.updateBar)
            self.thread.start()
        elif data_bar[0] == 0 and data_bar[1] == "error" and data_bar[2] == "กำลังดาวน์โหลดไฟล์":
            self.label_process.setText("ล้มเหลว")
            self.label_file.setText("ระบบทำการอัพเดตซอฟต์แวร์ล้มเหลว \nการดาวน์โหลดไฟล์ไม่สำเร็จ..!!")
            self.progressBar.hide()
            self.pushButton.show()

        elif data_bar[0] == 0 and data_bar[1] == "finish" and data_bar[2] == "กำลังอัพเดต":
            with open("path_file.txt", "r") as json_data:
                data = json_data.read()
                data_obj = json.loads(data)
                exe_name = data_obj['exe_name']
                json_data.close()
            ex = subprocess.call(exe_name, shell=True)
            if ex == 0:
                self.label_process.setText("สำเร็จ")
                self.label_file.setText("ระบบทำการอัพเดตซอฟต์แวร์เรียบเรียบเเล้ว")
                self.progressBar.hide()
                self.pushButton.show()
            else:
                self.label_process.setText("ล้มเหลว")
                self.label_file.setText("ระบบทำการอัพเดตซอฟต์แวร์ล้มเหลว \nถูกยกเลิกระหว่างการอัพเดต..!!")
                self.progressBar.hide()
                self.pushButton.show()
            os.remove(self.file_name)
            os.remove(exe_name)
        else:
            self.label_process.setText(data_bar[2])
            self.progressBar.setValue(data_bar[0])
            self.label_file.setText("ไฟล์ : " + data_bar[1])


class progressDownload(QThread):
    data_bar = pyqtSignal(object)

    def __init__(self, file_name):
        super(progressDownload, self).__init__()
        self.file_name = file_name

    def run(self):
        sleep(4)
        self.data_bar.emit([10, self.file_name, "กำลังดาวน์โหลดไฟล์"])
        with open("path_file.txt", "r") as json_data:
            data = json_data.read()
            data_obj = json.loads(data)
            url = data_obj['path_file']
            json_data.close()

        response = requests.get(url)
        if response.status_code != 200:
            self.data_bar.emit([0, "error", "กำลังดาวน์โหลดไฟล์"])
            return
        open(self.file_name, "wb").write(response.content)
        for i in range(15, 100):
            sleep(0.05)
            self.data_bar.emit([i, self.file_name, "กำลังดาวน์โหลดไฟล์"])
        self.data_bar.emit([0, "finish", "กำลังดาวน์โหลดไฟล์"])


class progressUpdateBar(QThread):
    data_bar = pyqtSignal(object)

    def __init__(self, file_name):
        super(progressUpdateBar, self).__init__()
        self.file_name = file_name

    def run(self):
        sleep(4)
        self.data_bar.emit([10, self.file_name, "กำลังอัพเดต"])
        zf = zipfile.ZipFile(self.file_name)
        uncompress_size = sum((file.file_size for file in zf.infolist()))
        extracted_size = 0
        for file in zf.infolist():
            extracted_size += file.file_size
            value = round(extracted_size * 100 / uncompress_size)
            self.data_bar.emit([value, file.filename, "กำลังอัพเดต"])
            zf.extract(file)
        self.data_bar.emit([0, "finish", "กำลังอัพเดต"])


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = Ui()
    sys.exit(app.exec_())
