import sys

from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QColor, QPainter, QPen
from PyQt5.QtWidgets import (
    QApplication,
    QPushButton,
    QLineEdit,
    QLabel,
    QWidget,
    QMainWindow,
    QTableWidgetItem,
    QTableWidget,
    QVBoxLayout,
)
from PyQt5 import uic  # Импортируем uic
from random import randint
import sys
from UI.ui_file import Ui_MainWindow

import sqlite3


def db_opener(func):
    def func_with_open(*args, **kwargs):
        con = sqlite3.connect("data/coffee.sqlite")
        pointer = con.cursor()

        def new_func(*args, **kwargs):
            result = func(*args, **kwargs, cur=pointer)
            con.commit()
            con.close()
            return result

        try:
            return new_func(*args, **kwargs)
        except Exception as e:
            print(e.__class__.__name__, e)

    return func_with_open


@db_opener
def add_coffee(*data, cur=None):
    cur.execute(
        f"""INSERT INTO coffee VALUES
    {data}"""
    )


@db_opener
def change_coffee(what="", value="", where="", cur=None):
    """меняет данные о клиенте поле {what} = {value}, id = {where}"""
    cur.execute(f"""UPDATE coffee SET {what} = '{value}' WHERE id = '{where}'""")


@db_opener
def get_from(what="*", where={}, fromdb="coffee", cur=None) -> list:
    """берёт данные из db
    what='*', where={}, fromdb='clientele'"""
    data = """"""
    if where:
        for i in where:
            data += (
                i + "=" + "'" + where[i] + "'" + " "
                if isinstance(where[i], str)
                else i + "=" + str(where[i]) + " "
            )
        result = cur.execute(f"""SELECT {what} FROM {fromdb} WHERE {data}""").fetchall()
    else:
        result = cur.execute(f"""SELECT {what} FROM {fromdb}""").fetchall()
    return list(result)


FIELD = ("id", "name", "roasting", "grains", "taste", "cost", "volume")
NAMING = (
    "ID",
    "название сорта",
    "степень обжарки",
    "молотый/в зернах",
    "описание вкуса",
    "цена",
    "объем упаковки",
)


class AddPartOrderInTable(QWidget):
    def __init__(self, *data):
        super().__init__()
        self.main = data[0]
        self.part = data[-1]
        self.setGeometry(30, 30, 700, 200)
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setGeometry(0, 0, 400, 400)
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(NAMING)
        self.tableWidget.setRowCount(1)
        if self.part != -1:
            for i, elem in enumerate(data[1]):
                self.tableWidget.setItem(0, i, QTableWidgetItem(elem))
            self.tableWidget.resizeColumnsToContents()
            self.tableWidget.itemSelectionChanged.connect(
                self.tableWidget.resizeColumnsToContents
            )
        self.data_send = QPushButton("Ок", self)
        self.data_send.clicked.connect(self.get_data)
        self.vbox = QVBoxLayout(self)
        self.vbox.addWidget(self.tableWidget)
        self.vbox.addWidget(self.data_send)

    def get_data(self):
        result = []
        for col in range(7):
            result.append(self.tableWidget.item(0, col).text())
        self.main.get_info(result, self.part)

        # self.main.layout.removeWidget(self.main.secondWidget)
        # self.main.secondWidget = QTableWidget()
        # self.main.layout.addWidget(self.main.secondWidget)
        # print(self.main.data)
        # return self.main.data


class Square1(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)  # Загружаем дизайн
        self.data = get_from()
        self.make_table()
        self.addCoffee.clicked.connect(self.add)
        self.changeCoffee.clicked.connect(self.change)

    def make_table(self):
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(NAMING )
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(self.data):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, value in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(value)))
        # self.tableWidget.resizeColumnsToContents()
        # self.tableWidget.setColumnWidth(0, 150)
        # self.tableWidget.setColumnWidth(1, 220)

    def showForm(self, data, row=-1):
        self.vvod = AddPartOrderInTable(self, data, row)
        self.vvod.show()

    def change(self):
        y = self.tableWidget.currentRow()
        data = []
        for i in range(7):
            data.append(str(self.tableWidget.item(y, i).text()))
        self.showForm(data, y)

    def add(self):
        self.showForm([])

    def get_info(self, data, row):
        if row == -1:
            data[0] = int(data[0])
            self.data.append(data)
            add_coffee(*data)
            self.make_table()
        else:
            data[0] = int(data[0])
            self.data[row] = data
            for i, el in enumerate(FIELD):
                change_coffee(el, data[i], data[0])

            self.make_table()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Square1()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
