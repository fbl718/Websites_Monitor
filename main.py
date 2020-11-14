import datetime
import os
import sys
import threading
from urllib.request import urlopen

import pyperclip
from PyQt5.QtWidgets import QApplication, QMainWindow, QInputDialog, QListWidgetItem, QMessageBox
from apscheduler.schedulers.blocking import BlockingScheduler

import Screen1


class MainCode(QMainWindow, Screen1.Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        Screen1.Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.Refresh.clicked.connect(self.refresh)
        self.Check_all.clicked.connect(self.check_all)
        self.Add.clicked.connect(self.add)
        self.checkBox.stateChanged.connect(self.auto_check)
        self.time_interval = 300
        self.Set_time_interval.clicked.connect(self.showDialog)
        self.Check.clicked.connect(self.check)
        self.checkBox.setText('Auto check (' + str(int(self.time_interval / 60)) + ' min)')
        self.checkBox.adjustSize()
        self.listWidget.itemDoubleClicked.connect(self.list_double_clicked)
        self.listWidget.itemClicked.connect(self.list_clicked)
        self.Delete.clicked.connect(self.list_delete)
        self.listWidget.itemSelectionChanged.connect(self.delete_enable)
        self.Input_dialog = QInputDialog(self.centralwidget)
        self.Url.textChanged.connect(self.add_enable)
        self.Duplicate.clicked.connect(self.duplicate)
        self.Clear.clicked.connect(self.clear)
        self.Message_box = QMessageBox(self.centralwidget)
        self.actionAbout_Author.triggered.connect(self.about_author)
        self.actionAbout.triggered.connect(self.about)
        self.actionHelp.triggered.connect(self.help)
        self.timer = threading.Timer(self.time_interval / 60, self.auto_check)
        self.scheduler=BlockingScheduler()
        self.scheduler.add_job(self.auto_check_helper,'interval',seconds=5)
        self.websites_list = []
        self.refresh()

    def refresh(self):
        self.listWidget.clear()
        with open('Websites.txt') as fp:
            lines = fp.read().splitlines()
            self.websites_list = lines
            for line in lines:
                item = QListWidgetItem(line)
                item.setToolTip('Double clicked to edit')
                self.listWidget.addItem(item)
            # self.listWidget.addItems(lines)
        self.statusbar.showMessage('Refresh successfully', 5000)

    def check_all(self):
        self.Log.clear()
        with open('Log.txt', 'a') as output_file:
            self.progressBar.setEnabled(True)
            self.progressBar.setMaximum(self.listWidget.count())
            self.progressBar.setValue(0)
            for index in range(0, self.websites_list.__len__()):
                try:
                    url = self.websites_list[index]
                    resp = urlopen(url, timeout=4)
                    code = resp.getcode()
                    if code == 200:
                        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        output_file.write('Time: ' + time + '\n')
                        output_file.write('Url: ' + url + '\n')
                        output_file.write('OK' + '\n\n')
                        self.Log.append('Time: ' + time)
                        self.Log.append('Url: ' + url)
                        self.Log.append('OK' + '\n')
                    else:
                        raise Exception(code)
                except Exception as e:
                    # output_file.write('Error occurred\n')
                    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    output_file.write('Time: ' + time + '\n')
                    output_file.write('Url: ' + url + '\n')
                    output_file.write('Error: ' + str(e) + '\n\n')
                    self.Log.append('Time: ' + time)
                    self.Log.append('Url: ' + url)
                    self.Log.append('Error: ' + str(e) + '\n')
                    # print('Time: ' + time + '\n' + 'Url: ' + url + '\n' + 'Message: ' + str(e))
                self.progressBar.setValue(index + 1)
        self.statusbar.showMessage('Check all successfully', 5000)

    def add(self):
        self.url_correct()
        if self.Url.text() != '':
            with open('Websites.txt', 'a') as fp:
                if os.path.getsize('Websites.txt') == 0:
                    fp.write(self.Url.text())
                else:
                    fp.write('\n' + self.Url.text())
            self.statusbar.showMessage('Add successfully', 5000)
        self.refresh()

    def auto_check(self):
        if self.checkBox.checkState():
            self.auto_check_helper()
            self.timer = threading.Timer(self.time_interval / 60, self.auto_check)
            next_time = datetime.datetime.now() + datetime.timedelta(seconds=self.time_interval/60)
            self.Check_time.setText('Next check time: ' + next_time.strftime('%Y-%m-%d %H:%M:%S'))
            self.Check_time.adjustSize()
            self.timer.start()
        else:
            self.timer.cancel()


    def auto_check_helper(self):
        with open('Log.txt', 'a') as output_file:
            for index in range(0, self.listWidget.count()):
                try:
                    url=self.websites_list[index]
                    # url = self.listWidget.item(index).text()
                    resp = urlopen(url, timeout=4)
                    code = resp.getcode()
                    if code != 200:
                        raise Exception(code)
                except Exception as e:
                    # output_file.write('Error occurred\n')
                    time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    output_file.write('Time: ' + time + '\n')
                    output_file.write('Url: ' + url + '\n')
                    output_file.write('Error: ' + str(e) + '\n\n')
                    self.Log.append('Time: ' + time)
                    self.Log.append('Url: ' + url)
                    self.Log.append('Error: ' + str(e) + '\n')
                    # print('Time: ' + time + '\n' + 'Url: ' + url + '\n' + 'Message: ' + str(e))
        self.statusbar.showMessage('Check all successfully', 5000)


    def showDialog(self):
        result, ok = self.Input_dialog.getInt(self, 'Set time interval', 'Time Interval (min):',
                                              int(self.time_interval / 60), min=1)
        if ok:
            self.time_interval = result * 60
            self.checkBox.setText('Auto check (' + str(int(self.time_interval / 60)) + ' min)')
            self.checkBox.adjustSize()

    def url_correct(self):
        url = self.Url.text()
        if not url.startswith('https://') and not url.startswith('http://') and url != '':
            self.Url.setText('http://' + url)

    def check(self):
        self.url_correct()
        url = self.Url.text()
        try:
            resp = urlopen(url, timeout=4)
            code = resp.getcode()
            if code != 200:
                raise Exception(code)
        except Exception as e:
            self.Url_status.setText('Error: ' + str(e))
            self.Url_status.adjustSize()
        else:
            self.Url_status.setText('OK')
            self.Url_status.adjustSize()

    def list_double_clicked(self):
        text = self.listWidget.currentItem().text()
        row = self.listWidget.row(self.listWidget.currentItem())
        result, ok = self.Input_dialog.getText(self, 'Rewrite url', 'Please enter new url here: ', text=text)
        # print(result)
        if ok:
            with open('Websites.txt', 'r+') as fp:
                content = fp.readlines()
            with open('Websites.txt', 'w+') as fp:
                if row == content.__len__() - 1:
                    content[row] = result
                else:
                    content[row] = result + '\n'
                fp.writelines(content)
            self.statusbar.showMessage('Edit successfully', 5000)
        self.refresh()

    def list_clicked(self):
        self.Url.setText(self.listWidget.currentItem().text())

    def list_delete(self):
        row = self.listWidget.row(self.listWidget.currentItem())
        with open('Websites.txt', 'r+') as fp:
            content = fp.readlines()
        with open('Websites.txt', 'w+') as fp:
            if row == content.__len__() - 1:
                del content[row]
                content[row - 1] = content[row - 1].replace('\n', '')
            else:
                del content[row]
            fp.writelines(content)
        self.statusbar.showMessage('Delete successfully', 5000)
        self.refresh()

    def delete_enable(self):
        self.Delete.setEnabled(self.listWidget.selectedItems().__len__() != 0)

    def add_enable(self):
        if self.Url.text() == '':
            self.Check.setEnabled(False)
            self.Add.setEnabled(False)
        else:
            self.Check.setEnabled(True)
            self.Add.setEnabled(self.Url.text() not in self.websites_list)

    def duplicate(self):
        pyperclip.copy(self.Log.toPlainText())

    def clear(self):
        self.Log.clear()

    def about(self):
        self.Message_box.about(self, "About Websites Monitor",
                               "This is a program developed by Fang Baole to automatically check whether the "
                               "connection every website in the list is good. If not, the error will be recorded in "
                               "the log error.\n\nVersion: V1.0\nUpdate time: 2019-12-31")

    def about_author(self):
        self.Message_box.about(self, "About Author", "中远海运科技股份有限公司 云数据中心 方宝乐\n联系方式：fbl718@sjtu.edu.cn")

    def help(self):
        self.Message_box.about(self, "Help",
                               '1. When the program is launched, website list is automatically refreshed.\n2. Click '
                               '"Refresh" button to refresh the website list.\n3. Click "Check all" button to check '
                               'whether all the connections of all the websites in the website list are good. If '
                               'there are any errors, they will be recorded in the error log and in the file '
                               '"Log.txt".\n4. Check the checkbox to automatically check the status of all websites '
                               'in the website list every time interval.\n5. Click "Set time interval" button to set '
                               'the time interval of auto check.\n6. Click "Add" button to add a new website to the '
                               'website list. It should be non-empty and different from existing websites.\n7. Click '
                               '"Check" button to check the status of the website inputted in the textbox.\n8. Click '
                               'an element in the website list to put it in the textbox.\n9. Double click an element '
                               'in the website list to edit its url.\n10. Click "Delete" button to delete the '
                               'selected website in the website list.\n11. Click "Copy" button to copy the error log '
                               'to the clipboard.\n12. Click "Clear" button to clear the error log. Be aware that it '
                               'will not delete anything in the file "Log.txt".')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    md = MainCode()
    md.show()
    sys.exit(app.exec_())
