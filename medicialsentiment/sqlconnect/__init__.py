import logging
import pymysql


class SQLConnect(object):
    def __init__(self, host, db_name, username, password, charset):
        self.__host = host
        self.__db_name = db_name
        self.__username = username
        self.__password = password
        self.__charset = charset
        self.__connection = None

    def connect(self):
        self.__connection = pymysql.connect(host=self.__host,
                                            db=self.__db_name,
                                            user=self.__username,
                                            password=self.__password,
                                            charset=self.__charset,
                                            cursorclass=pymysql.cursors.DictCursor)

    def insert_search_result_score(self, search_id, link, title, result_score, sentences, sentences_score):
        with self.__connection.cursor() as cursor:
            # Create a new record
            sql = "INSERT INTO `searchresult` (`SearchId`, `SearchResultRate`, `Link`, `Title`) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (search_id, result_score, link, title))
            result_id = cursor.lastrowid

            for counter, element in enumerate(sentences):
                sql2 = "INSERT INTO `sentence` (`search_result_id`, `sentences`, `sentence_grade`) VALUES (%s, %s, %s)"
                cursor.execute(sql2, (result_id, element, sentences_score[counter]))
        self.__connection.commit()

