from datetime import timedelta, datetime
import sys
#from PySide2.QtWidgets import QApplication, QPushButton
from PyQt5.QtWidgets import (QWidget, QLabel, QTextEdit, QGridLayout, QApplication, QPushButton, QDesktopWidget)
#from PySide2.QtCore import Slot
import psycopg2

conn = psycopg2.connect(dbname='postgres', user='user', host="192.168.0.103", password = "user")
cursor = conn.cursor()



class Book:

    def __init__(self, id, name, author, year, publ, whos = 0, date = datetime(2000, 1, 1) ):
        self.id = id
        self.name = name
        self.author = author
        self.year = year
        self.publ = publ
        self.whos = whos
        self.date = date

    def __str__(self):

        if self.whos ==0:
            date = ""
            whos = "Доступна"
        else:
            date = "("+ str(self.date) + ")"
            whos = "Взята пользователем с id "+ str(self.whos)

        return f"Идентификатор: {self.id}\nНазвание: {self.name}\nАвтор: {self.author}\nИздательство: {self.publ}\nГод издания: {self.year}\nДоступность: {whos}\
 {str(date)}"

class User:
    count = 0

    def __init__(self, id, name, register_date , books_is_in_hands = 0, books_alltime = 0, id_book = 0):
        if register_date==None:
            self.register_date = datetime.now()
        else:
            self.register_date = register_date
        if (id==0):
            User.count+=1
            self.id = User.count
        else:
            self.id = id
        self.name = name
        self.books_now = books_is_in_hands
        self.books_alltime = books_alltime
        self.id_book = id_book

    def __str__(self):
        return f"Идентификатор: {self.id}\nИмя читателя: {self.name}\nДата регистрации {self.register_date}\nКниг на руках: {self.books_now}\nВзято книг за всё время: {self.books_alltime} Сейчас на руках: {self.id_book}"

def find_user_by_id(id, mas_users):
    for i in mas_users:
        if i.id == id:
            return i
    return None

def find_book_by_id(id, mas_book):
    for i in mas_book:
        if i.id == id:
            return i
    return None

def bring_book(mas_book, mas_user,  id_book, id_user):
    user = find_user_by_id(id_user, mas_user) #type: User
    book = find_book_by_id(id_book, mas_book) #type: Book
    if user!=None and book!=None:
        if user.id_book == 0 and book.whos == 0:
            book.whos  = user.id
            #book.date = datetime.now()
            book.date = datetime(2001, 1, 1)
            user.books_now +=1
            user.books_alltime+=1
            user.id_book = book.id
            #query = f"UPDATE book SET date = '{book.date}' WHERE id = {book.id}"
            cursor.execute("update book set date = %s, whos = %s where id = %s", (book.date,book.whos, book.id))
            cursor.execute("update users set id_book = %s, books_now = %s, books_alltime = %s where id = %s", (book.id, user.books_now, user.books_alltime, user.id))
            str1  = f"\n Пользователь с id {id_user} взял книгу {book.name} автора {book.author}"
            conn.commit()
            return str1
        else:
            str1 = f"\n Пользователь с id {id_user} уже взял книгу и/или книга с id {book.id} на руках"
            return str1


def return_book(mas_book, mas_user,  id_book, id_user):
    user = find_user_by_id(id_user, mas_user) #type: User
    book = find_book_by_id(id_book, mas_book) #type: Book
    if user!=None and book!=None:
        if user.id_book == book.id and book.whos == user.id:
            book.whos  = 0
            book.date = datetime(2000, 1, 1)
            user.books_now = 0
            user.id_book = 0
            cursor.execute("update book set whos = 0, date = %s,  where id = %s", (book.date, book.id))
            cursor.execute("update users set id_book = 0, books_now = 0, where id = user.id", (user.id))
            cursor.commit()
            str1 = f"\n Пользователь с id {id_user} вернул книгу {book.name} автора {book.author}"
            return str1
        else:
            str1 = f"\n У пользователя с данным id {id_user} нет на руках книги {book.name} автора {book.author}"
            return str1

def list_of_debtors(mas_book, mas_user):
    maxdate =timedelta(days = 10)
    mas_debtors = []
    nowdate = datetime.now()
    for i in mas_book:
        if i.whos!=0:
            if i.date+maxdate<nowdate:
                b = find_user_by_id(i.whos, mas_user)
                mas_debtors.append(b)
    #print('Cписок должников: ')
    str1 = "\n"+"Cписок должников: "+"\n"
    for i in mas_debtors:
        str1+=str(i)+"\n"+"\n"
    return(str1)

Bookmas = []
# Выполняем запрос.
cursor.execute('SELECT * FROM book')
measures = cursor.fetchall()
for record in measures:
    # print(record)
    tempBook = Book(record[0],
                    record[1],
                    record[2],
                    record[3],
                    record[4],
                    record[5],
                    record[6])
    Bookmas.append(tempBook)

Usermas = []
cursor.execute('SELECT * FROM users')
users = cursor.fetchall()
for record in users:
    # print(record)
    tempUser = User(record[0],
                    record[1],
                    record[2],
                    record[3],
                    record[4],
                    record[5])
    print(tempUser)
    Usermas.append(tempUser)

# data = datetime(2020, 1, 1)
# book1 = Book(1, 'Над пропастью во ржи','Cэлинжер', 1980, "Эксмо")
# book2 = Book(2, 'Над пропастью во ржи','Cэлинжер', 1980, "Эксмо")
# mas_book  = [book1, book2]
# user1 = User('Ковалев', data)
# user2 = User('Иванов', data)
# mas_user = [user1, user2]

# print('User1: ')
# print(user1)
# bring_book(mas_book, mas_user, 2, 2)
# print('User2: ')
# print(user2)

print(list_of_debtors(Bookmas, Usermas))
print()


# @Slot()
# def print_list_of_debtors():
#     list_of_debtors(mas_book, mas_user)
#
# app = QApplication(sys.argv)
# button = QPushButton("Click me")
#
# button.clicked.connect(print_list_of_debtors)
#
# button.show()
# app.exec_()




class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()
        self.bookid = None
        self.userid=None

    def initUI(self):
        self.I = 0
        label1 = QLabel('Логи')
        label2 = QLabel('Id книги')
        label3 = QLabel('Id пользователя')
        self.textEdit1 = QTextEdit()
        self.textEdit1.setReadOnly(True)
        self.textEdit2 = QTextEdit()
        self.textEdit3 = QTextEdit()
        btn1 = QPushButton('Список должников')
        btn2 = QPushButton('Взять книгу')
        btn3 = QPushButton('Вернуть книгу')
        btn4 = QPushButton('Очистить')
        btn5 = QPushButton('Закончить ввод')
        btn1.clicked.connect(self.buttonClicked1)
        btn2.clicked.connect(self.buttonClicked2)
        btn3.clicked.connect(self.buttonClicked3)
        btn4.clicked.connect(self.textEdit1.clear)
        btn5.clicked.connect(self.buttonClicked5)
        grid = QGridLayout()
        grid.setSpacing(10)
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


        self.setLayout(grid)
        x = QDesktopWidget().availableGeometry().center().x()
        y = QDesktopWidget().availableGeometry().center().y()
        # self.setGeometry(300, 300, 500, 500)
        width = 500
        height = 500
        self.setGeometry(x-width/2, y-height/2, 500, 500)
        self.setWindowTitle('Review')
        self.show()


    def buttonClicked1(self):
        self.textEdit1.insertPlainText(list_of_debtors(Bookmas, Usermas))

    def buttonClicked2(self):
        # pass
        # value = self.textEdit2.toPlainText()
        # value = int(value)
        self.textEdit1.insertPlainText(bring_book(Bookmas, Usermas, self.bookid, self.userid))

    def buttonClicked3(self):
        self.textEdit1.insertPlainText(return_book(Bookmas, Usermas,  self.bookid, self.userid))

    def buttonClicked5(self):
        value = self.textEdit2.toPlainText()
        self.bookid = int(value)
        value = self.textEdit3.toPlainText()
        self.userid = int(value)

        #self.buttonClicked2(self.value)


app = QApplication(sys.argv)
ex = Example()
sys.exit(app.exec_())
conn.close()   # закрываем соединение с базой