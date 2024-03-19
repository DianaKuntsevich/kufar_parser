import psycopg2
from environs import Env
from psycopg2._psycopg import cursor
from psycopg2 import extras
from faker import Faker
from random import randint

env = Env()
env.read_env()

DBNAME = env('DBNAME')
DBUSER = env('DBUSER')
DBPASSWORD = env('DBPASSWORD')
DBHOST = env('DBHOST')
DBPORT = env('DBPORT')


class DBPostgres:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __init__(self, dbname, user, password, host, port):
        self.__dbname = dbname
        self.__user = user
        self.__password = password
        self.__host = host
        self.__port = port


    def fetch_one(self, query: str, data=None, factory=None, clean=False):
        try:
            with self.__connect_db(factory) as cur:
                self.__execute(cur, query, data)
                return self.__fetch(cur, clean)
        except (Exception, psycopg2.Error) as error:
            self.__error(error)


    def fetch_all(self, query: str, data=None, factory=None):
        try:
            with self.__connect_db(factory) as cur:
                self.__execute(cur, query, data)
                return cur.fetchall()
        except (Exception, psycopg2.Error) as error:
            self.__error(error)


    def update_query(self, query:str, data=None, message='OK'):
        try:
            with self.__connect_db() as cur:
                self.__execute(cur, query, data)
                print(message)
        except (Exception, psycopg2.Error) as error:
            self.__error(error)

    def __connect_db(self, factory: str = None):
        '''

        :param factory:
        :return: cursor
        '''
        conn = psycopg2.connect(
            dbname=self.__dbname,
            user=self.__user,
            password=self.__password,
            host=self.__host,
            port=self.__port
        )
        conn.autocommit = True

        if factory == 'dict':
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        elif factory == 'list':
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        else:
            cur = conn.cursor()

        return cur

    @staticmethod
    def __execute(cur: cursor, query: str, data=None):
        if data:
            if isinstance(data, list):
                cur.executemany(query, data)
            else:
                cur.execute(query, data)
        else:
            cur.execute(query)


    @staticmethod
    def __fetch(cur: cursor, clean):
        if clean:
            fetch = cur.fetchone()[0]
        else:
            fetch = cur.fetchone()

        return fetch

    @staticmethod
    def __error(error):
        print(error)

# db = DBPostgres(DBNAME, DBUSER, DBPASSWORD, DBHOST, DBPORT)
# data = [('Maria', 25), ('Olga', 30)]
# db.update_query('''INSERT INTO user_test(name, age) VALUES (%s, 45)''', ('Vasiliy',))

# data = db.fetch_all('''SELECT * FROM user_test WHERE age = %s''', (30,), factory='dict')
# print([dict(i) for i in data])

# data = db.fetch_one('''SELECT name FROM user_test WHERE id = %s''', (5,), clean=True)
# print(data)
db = DBPostgres(DBNAME, DBUSER, DBPASSWORD, DBHOST, DBPORT)

# db.update_query('''CREATE TABLE person(
# id serial PRIMARY KEY,
# name varchar(100),
# surname varchar(100),
# age integer
# );
# CREATE TABLE tel(
# id serial PRIMARY KEY,
# number varchar(15),
# person_id integer REFERENCES person(id)
# )''')
fake = Faker('RU')
person = []
for i in range(500):
    names = fake.name().split()
    age = randint(1, 70)
    if i % 2:
        tel = [f'+375{randint(1000000, 9000000)}' for j in range(5)]
    else:
        tel = []
    name = names[1]
    surname = names[0]
    person.append((name, surname, age, tel))
# Сохранение в БД данных (долгое)
# for i in person:
#     db.update_query('''INSERT INTO person(name, surname, age) VALUES (%s, %s, %s)''', i[:-1])
#     for t in i[-1]:
#         db.update_query('''INSERT INTO tel(number, person_id) VALUES (%s, (SELECT id FROM person WHERE name= %s))''', (t, i[0]))


# Хороший быстрый запрос на добавление в БД ( не заботает с пустым списком)
# for i in person:
#     db.update_query('''WITH person_id as (INSERT INTO person(name, surname, age) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING RETURNING id)
#     INSERT INTO tel(number, person_id) VALUES (unnest(%s), (SELECT id FROM person_id)) ON CONFLICT DO NOTHING
#     ''', i)

for i in person:
    db.update_query('''WITH person_id as (INSERT INTO person(name, surname, age) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING RETURNING id) 
    INSERT INTO tel(number, person_id) VALUES (unnest(COALESCE(%s, ARRAY[]::text[])), (SELECT id FROM person_id)) ON CONFLICT DO NOTHING
    ''', i)
