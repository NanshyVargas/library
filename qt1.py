import sys
import proto1
from PyQt5.QtWidgets import (QWidget, QLabel, QTextEdit, QGridLayout, QApplication, QPushButton, QDesktopWidget)


class Example(QWidget):

    def templateAction(self, userId, bookId):
        '''Автозаполнение заранее определенными значениями'''
        self.textEdit2.insertPlainText(str(userId))
        self.textEdit3.insertPlainText(str(bookId))

    def __init__(self, conn, cursor):
        super().__init__()
        self.initUI()
        self.bookid = None
        self.userid=None
        self.cursor = cursor
        self.conn = conn

    def initUI(self):
        self.I = 0
        label1 = QLabel('Логи')
        label2 = QLabel('Id книги')
        label3 = QLabel('Id пользователя')
        self.textEdit1 = QTextEdit()
        """Сюда пишем логи"""
        self.textEdit1.setReadOnly(True)
        """Нельзя редактировать"""
        self.textEdit2 = QTextEdit()
        """Для ввода id книги"""
        self.textEdit3 = QTextEdit()
        """Для ввода id читателя"""
        btn1 = QPushButton('Список должников')
        btn2 = QPushButton('Взять книгу')
        btn3 = QPushButton('Вернуть книгу')
        btn4 = QPushButton('Очистить')
        btn5 = QPushButton('Закончить ввод')
        btn1.clicked.connect(self.buttonClicked1)
        btn2.clicked.connect(self.buttonClicked2)
        btn3.clicked.connect(self.buttonClicked3)
        btn4.clicked.connect(self.textEdit1.clear)
        """Стираем все логи с экрана"""
        btn5.clicked.connect(self.buttonClicked5)
        grid = QGridLayout()
        grid.setSpacing(10)
        #Расположение элементов
        grid.addWidget(label1, 0, 0, 1, 3)
        grid.addWidget(self.textEdit1, 1, 0, 1, 4)
        grid.addWidget(btn1, 2, 0)
        grid.addWidget(btn2, 2, 1)
        grid.addWidget(btn3, 2, 2)
        grid.addWidget(btn4, 2, 3)
        grid.addWidget(label2, 3, 1, 1, 1)
        grid.addWidget(self.textEdit2, 4, 1, 1, 1)
        grid.addWidget(label3, 3, 2, 1, 1)
        grid.addWidget(self.textEdit3, 4, 2, 1, 1)
        grid.addWidget(btn5, 5, 2)
        self.templateAction(1, 1)

        self.setLayout(grid)
        x = QDesktopWidget().availableGeometry().center().x()
        y = QDesktopWidget().availableGeometry().center().y()
        width = 500
        height = 500
        self.setGeometry(x-width/2, y-height/2, 500, 500)
        self.setWindowTitle('Review')
        self.show()


    def buttonClicked1(self):
        """Вывод списка должников"""
        self.textEdit1.insertPlainText(proto1.list_of_debtors(proto1.Bookmas, proto1.Usermas))

    def buttonClicked2(self):
        """Вывод логов для операции "Взять книгу" """
        self.textEdit1.insertPlainText(proto1.bring_book(proto1.Bookmas, proto1.Usermas, self.bookid, self.userid, self.conn, self.cursor))

    def buttonClicked3(self):
        """Вывод логов для операции "Вернуть книгу" """
        self.textEdit1.insertPlainText(proto1.return_book(proto1.Bookmas, proto1.Usermas,  self.bookid, self.userid,  self.conn, self.cursor))

    def buttonClicked5(self):
        """Закончить ввод, обработать данные"""
        value = self.textEdit2.toPlainText()
        self.bookid = int(value)
        value = self.textEdit3.toPlainText()
        self.userid = int(value)

conn, cursor = proto1.openconn()
app = QApplication(sys.argv)
ex = Example(conn, cursor)
sys.exit(app.exec_())

