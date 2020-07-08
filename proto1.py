from datetime import timedelta, datetime
import psycopg2

def openconn():
    '''Инициирует соединение с базой'''
    conn = psycopg2.connect(dbname='postgres', user='user', host="192.168.0.103", password = "user")
    cursor = conn.cursor()
    return conn, cursor



class Book:
    '''Класс "Book"'''
    def __init__(self, id, name, author, year, publ, whos = 0, date = datetime(2000, 1, 1) ):
        self.id = id
        self.name = name
        '''Название книги'''
        self.author = author
        '''Автор'''
        self.year = year
        '''Год издания'''
        self.publ = publ
        '''Издательство'''
        self.whos = whos
        '''У кого на руках - id читателя'''
        self.date = date
        '''С какого числа на руках'''


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
    '''Класс "Пользователь - Читатель библиотеки'''
    #count = 0

    def __init__(self, id, name, register_date , books_now = 0, books_alltime = 0, id_book = 0):
        if register_date==None:
            self.register_date = datetime.now()
        else:
            self.register_date = register_date
        self.id = id
        self.name = name
        self.books_now = books_now
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

def bring_book(mas_book, mas_user,  id_book, id_user, conn, cursor):
    '''Функция "Взять книгу"'''
    user = find_user_by_id(id_user, mas_user) #type: User
    book = find_book_by_id(id_book, mas_book) #type: Book
    if user!=None and book!=None:
        if user.id_book == 0 and book.whos == 0:
            book.whos  = user.id
            book.date = datetime(2001, 1, 1)
            '''Дата по умолчанию'''
            user.books_now +=1
            user.books_alltime+=1
            user.id_book = book.id #Добавим id книги к записи читателя
            cursor.execute("update book set date = %s, whos = %s where id = %s", (book.date,book.whos, book.id))
            '''Выполняется запрос к базе, чтобы обновить таблицу Book, добавив новые данные'''
            cursor.execute("update users set id_book = %s, books_now = %s, books_alltime = %s where id = %s", (book.id, user.books_now, user.books_alltime, user.id))
            '''Выполняется запрос к базе, чтобы обновить таблицу Users, добавив новые данные'''
            str1  = f"\n Пользователь с id {id_user} взял книгу {book.name} автора {book.author}"
            cursor.execute("insert into events (operation_id, logs) values (1, %(log)s)", {'log':str1})
            '''Выполняется запрос к базе, чтобы обновить таблицу Events, пишем логи'''
            conn.commit()
            """Для того, чтоб работал update"""
            return str1
        else:
            str1 = f"\n Пользователь с id {id_user} уже взял книгу и/или книга с id {book.id} на руках"
            return str1


def return_book(mas_book, mas_user,  id_book, id_user,conn, cursor):
    '''Функция "Вернуть книгу"'''
    user = find_user_by_id(id_user, mas_user) #type: User
    book = find_book_by_id(id_book, mas_book) #type: Book
    if user!=None and book!=None:
        if user.id_book == book.id and book.whos == user.id:
            book.whos  = 0
            book.date = datetime(2000, 1, 1)
            user.books_now = 0
            user.id_book = 0
            cursor.execute("update book set whos = 0, date = %(date)s  where id = %(id)s", {'date':book.date, 'id': book.id})
            '''Выполняется запрос к базе, чтобы обновить таблицу Book, освобождаем книгу'''
            cursor.execute("update users set id_book = 0, books_now = 0 where id = %(id)s", {'id': user.id})
            '''Выполняется запрос к базе, чтобы обновить таблицу Users, возвращаем книгу, на руках - 0'''
            str1 = f"\n Пользователь с id {id_user} вернул книгу {book.name} автора {book.author}"
            cursor.execute("insert into events (operation_id, logs) values (2, %(log)s)", {'log': str1})
            '''Выполняется запрос к базе, чтобы обновить таблицу Events, пишем логи'''
            conn.commit()
            """Для того, чтоб работал update"""
            return str1
        else:
            str1 = f"\n У пользователя с данным id {id_user} нет на руках книги {book.name} автора {book.author}"
            return str1

def list_of_debtors(mas_book, mas_user):
    '''Выводит список читателей, у которых книга на руках дольше установленного (10 дней) срока'''
    maxdate =timedelta(days = 10)
    mas_debtors = []
    nowdate = datetime.now()
    for i in mas_book:
        if i.whos!=0:
            if i.date+maxdate<nowdate:
                b = find_user_by_id(i.whos, mas_user)
                mas_debtors.append(b)
    str1 = "\n"+"Cписок должников: "+"\n"
    for i in mas_debtors:
        str1+=str(i)+"\n"+"\n"
    return(str1)


def connectionbase():
    """Считываем данные из базы и записываем в объекты классов"""
    conn, cursor = openconn()
    Bookmas = []
    # Выполняем запрос.
    cursor.execute('SELECT * FROM book')
    measures = cursor.fetchall()
    for record in measures:
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
        tempUser = User(record[0],
                        record[1],
                        record[2],
                        record[3],
                        record[4],
                        record[5])
        Usermas.append(tempUser)
    return Usermas, Bookmas

Usermas, Bookmas = connectionbase()