import logging
from urllib.parse import urlparse
import pymysql


class SQLConnect(object):
    def __init__(self, host, db_name, username, password, charset):
        self.__host = host
        self.__db_name = db_name
        self.__username = username
        self.__password = password
        self.__charset = charset
        self.__connection = None
        self.__whitelist = []

    def connect(self):
        self.__connection = pymysql.connect(host=self.__host,
                                            db=self.__db_name,
                                            user=self.__username,
                                            password=self.__password,
                                            charset=self.__charset,
                                            cursorclass=pymysql.cursors.DictCursor)
        with self.__connection.cursor() as cursor:
            sql = "SELECT * FROM `WhiteList`"
            cursor.execute(sql)
            self.__whitelist = cursor.fetchall()

    def extract_domain(self, url, remove_http=True):
        uri = urlparse(url)
        if remove_http:
            domain_name = f"{uri.netloc}"
        else:
            domain_name = f"{uri.netloc}://{uri.netloc}"
        return domain_name

    def get_white_list_id(self, link):
        for index, white in enumerate(self.__whitelist):
            if self.extract_domain(white["WhiteListLink"]) == self.extract_domain(link):
                return white["WhiteListId"]
        return 0

    def insert_search_result_score(self, search_id, link, title, result_score, sentences, sentences_score):
        with self.__connection.cursor() as cursor:
            # Create a new record
            w_id = self.get_white_list_id(link)
            sql = "INSERT INTO `searchresult` (`SearchId`, `SearchResultRate`, `Link`, `Title`, `WhiteListId`) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (search_id, result_score, link, title, w_id))
            result_id = cursor.lastrowid

            for counter, element in enumerate(sentences):
                sql2 = "INSERT INTO `sentence` (`search_result_id`, `sentences`, `sentence_grade`) VALUES (%s, %s, %s)"
                cursor.execute(sql2, (result_id, element, sentences_score[counter]))
        self.__connection.commit()
