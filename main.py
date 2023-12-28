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
)
from PyQt5 import uic  # Импортируем uic
from random import randint
import sys

import sqlite3


def db_opener(func):
    def func_with_open(*args, **kwargs):
        con = sqlite3.connect("coffee.sqlite")
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
    cur.execute(f"""UPDATE clientele SET {what} = '{value}' WHERE id = '{where}'""")


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


class Square1(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("main.ui", self)  # Загружаем дизайн
        self.data = get_from()
        self.make_table()

    def make_table(self):
        self.tableWidget.setColumnCount(7)
        self.tableWidget.setHorizontalHeaderLabels(
            (
                "ID",
                "название сорта",
                "степень обжарки",
                "молотый/в зернах",
                "описание вкуса",
                "цена",
                "объем упаковки",
            )
        )
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(self.data):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, value in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(value)))
        # self.tableWidget.resizeColumnsToContents()
        # self.tableWidget.setColumnWidth(0, 150)
        # self.tableWidget.setColumnWidth(1, 220)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = Square1()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
