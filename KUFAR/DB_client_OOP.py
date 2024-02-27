import psycopg2
from environs import Env
from psycopg2 import extras

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

    def __connect_db(self, factory: str=None):
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